import asyncio
import json
import re
from dataclasses import dataclass, field
from typing import List, Literal, Optional, Union

import httpx
import websockets

API_BASE_URL = "https://monitor-api.tweet-catcher.com:9999/pro"
WSS_URL = "ws://monitor-api.tweet-catcher.com:42069"


@dataclass
class PingRegex:
    regex: re.Pattern

    def __post_init__(self):
        if not isinstance(self.regex, re.Pattern):
            raise ValueError(
                "The `regex` argument must be a compiled regex pattern.")


@dataclass
class PingKeywords:
    negative: List[str]
    positive: List[str]

    def __post_init__(self):
        if len(self.negative) == 0 and len(self.positive) == 0:
            raise ValueError(
                "At least one keyword (positive or negative) must be provided.")

        if not all(isinstance(keyword, str) for keyword in self.negative):
            raise ValueError(
                "All elements in the `negative` list must be strings.")

        if not all(isinstance(keyword, str) for keyword in self.positive):
            raise ValueError(
                "All elements in the `positive` list must be strings.")


@dataclass
class CreateTaskArgs:
    username: str
    options: List[str] = field(default_factory=lambda: [
                               "posts", "retweets", "replies", "following", "userUpdates", "ocr"])
    notification: Literal["discord", "telegram",
                          "webhook", "websocket"] = "discord"

    webhook: Optional[str] = None
    webhook_posts: Optional[str] = None
    webhook_following: Optional[str] = None
    webhook_userUpdates: Optional[str] = None

    chatId: Optional[str] = None
    chatId_posts: Optional[str] = None
    chatId_following: Optional[str] = None
    chatId_userUpdates: Optional[str] = None

    differentWebhooks: bool = False
    ping: Literal["everyone", "here", "role", "none"] = "none"
    roleId: Optional[str] = None
    pingKeywords: Optional[Union[PingRegex, PingKeywords]] = None
    start: bool = False

    def __post_init__(self):
        if not isinstance(self.username, str) or not self.username.strip():
            raise ValueError(
                "The `username` argument must be a non-empty string.")

        if len(self.options) == 0:
            raise ValueError("At least one option must be selected.")

        if "ocr" in self.options:
            required_options = {"posts", "retweets", "replies"}
            if not any(opt in self.options for opt in required_options):
                raise ValueError(
                    "The `ocr` option requires at least one of `posts`, `retweets`, or `replies`.")

        if self.notification not in ["discord", "telegram", "webhook", "websocket"]:
            raise ValueError("Invalid notification type.")

        if self.notification == "discord":
            if not self.differentWebhooks and not self.webhook:
                raise ValueError(
                    "The `webhook` argument is required when using the `discord` notification type (unless `differentWebhooks` is True).")

        if self.notification == "webhook":
            if not self.webhook:
                raise ValueError(
                    "The `webhook` argument is required when using the `webhook` notification type.")

        if self.notification == "telegram":
            if not self.differentWebhooks and not self.chatId:
                raise ValueError(
                    "The `chatId` argument is required when using the `telegram` notification type.")

        if self.ping == "role" and not self.roleId:
            raise ValueError(
                "The `roleId` argument is required when using the `role` ping type.")

        if self.pingKeywords:
            if not isinstance(self.pingKeywords, (PingRegex, PingKeywords)):
                raise ValueError(
                    "The `pingKeywords` argument must be an instance of `PingRegex` or `PingKeywords`.")

        if self.differentWebhooks:
            if self.notification == "discord":
                if not (self.webhook_posts and self.webhook_following and self.webhook_userUpdates):
                    raise ValueError(
                        "`webhook-posts`, `webhook-following`, and `webhook-userUpdates` are required when using `differentWebhooks` with `discord`.")
            elif self.notification == "telegram":
                if not (self.chatId_posts and self.chatId_following and self.chatId_userUpdates):
                    raise ValueError(
                        "`chatId-posts`, `chatId-following`, and `chatId-userUpdates` are required when using `differentWebhooks` with `telegram`.")
            else:
                raise ValueError(
                    "The `differentWebhooks` argument can only be used with the `discord` or `telegram` notification types.")

    def __build_payload__(self):
        payload = {
            "user": self.username,
            "options": self.options,
            "notification": self.notification,
            "start": self.start
        }

        if self.webhook:
            payload["webhook"] = self.webhook

        if self.chatId:
            payload["chatId"] = self.chatId

        if self.differentWebhooks:
            payload["differentWebhooks"] = True
            if self.notification == "discord":
                payload["webhook-posts"] = self.webhook_posts
                payload["webhook-following"] = self.webhook_following
                payload["webhook-userUpdates"] = self.webhook_userUpdates
            elif self.notification == "telegram":
                payload["chatId-posts"] = self.chatId_posts
                payload["chatId-following"] = self.chatId_following
                payload["chatId-userUpdates"] = self.chatId_userUpdates

        if self.ping != "none":
            payload["ping"] = self.ping
            if self.roleId:
                payload["roleId"] = self.roleId

        if self.pingKeywords:
            if isinstance(self.pingKeywords, PingKeywords):
                payload["pingKeywords"] = {
                    "n": self.pingKeywords.negative,
                    "p": self.pingKeywords.positive
                }
                payload["useRegex"] = False
            else:
                payload["pingKeywords"] = {
                    "regex": self.pingKeywords.regex.pattern,
                    "isRegex": True
                }
                payload["useRegex"] = True

        return payload


class TweetCatcher:
    def __init__(self, api_token: str):
        self.api_token = api_token

        self.session = httpx.AsyncClient(headers={
            "Authorization": api_token
        })
        self.websocket = None
        self.websocket_messages = asyncio.Queue()
        self.heartbeat_interval = 30_000
        self.running = False

        self.listen_task = None
        self.heartbeat_task = None
        self.thread_exception = None

    async def heartbeat_handler(self):
        while self.running:
            try:
                await self.send_heartbeat()
                await asyncio.sleep(self.heartbeat_interval / 1000)
            except Exception as e:
                self.thread_exception = e
                break

    async def send_heartbeat(self):
        await self.websocket.send(json.dumps({
            "op": 1
        }))

    async def connect(self):
        self.websocket = await websockets.connect(WSS_URL)

        async with asyncio.timeout(60):
            while True:
                wss_data = json.loads(await self.websocket.recv())
                match wss_data.get("op", -1):
                    case 3:
                        raise Exception(
                            f"Failed to init websocket connection: server returned: {wss_data.get('text', 'Unknown error')}")
                    case 4:
                        await self.websocket_messages.put(wss_data)
                        self.heartbeat_task = asyncio.create_task(self.heartbeat_handler())
                        break
                    case 10:
                        await self.websocket.send(json.dumps({
                            "op": 2,
                            "token": self.api_token
                        }))
                    case _:
                        pass

    async def start(self):
        self.running = True
        await self.connect()
        self.listen_task = asyncio.create_task(self.listen())

    async def listen(self):
        while self.running:
            try:
                message = json.loads(await self.websocket.recv())
                if message.get("op") == 3:
                    raise Exception(
                        f"WebSocket connection closed: {message.get('text', 'Unknown error')}")
                await self.websocket_messages.put(message)
            except Exception as e:
                self.thread_exception = e

    async def stop(self):
        self.running = False
        try:
            await self.websocket.close()
        except: pass
        try:
            self.listen_task.cancel()
        except: pass
        try:
            self.heartbeat_task.cancel()
        except: pass

    async def get_message(self):
        if self.thread_exception:
            raise self.thread_exception

        return await self.websocket_messages.get()

    async def do_request(self, url):
        resp = await self.session.get(url)
        resp.raise_for_status()

        resp = resp.json()

        if isinstance(resp, dict) and resp.get("error"):
            raise Exception(f"Failed to do request: {resp['message']}")

        return resp

    async def get_user_info(self):
        return await self.do_request(f"{API_BASE_URL}/info")

    async def get_tasks(self):
        return await self.do_request(f"{API_BASE_URL}/tasks-list")

    async def create_task(self, args: CreateTaskArgs):
        payload = args.__build_payload__()
        resp = await self.session.post(f"{API_BASE_URL}/add-task", json=payload)
        resp.raise_for_status()
        resp = resp.json()

        if resp.get("error"):
            raise Exception(f"Failed to create task: {resp['message']}")

        return resp

    async def start_task(self, task_id: int):
        resp = await self.session.post(f"{API_BASE_URL}/start-task", json={"id": task_id})
        resp.raise_for_status()
        resp = resp.json()

        if resp.get("error"):
            raise Exception(f"Failed to start task: {resp['message']}")

        return resp

    async def edit_task(self, task_id: int, args: CreateTaskArgs):
        payload = args.__build_payload__()
        payload["id"] = task_id

        resp = await self.session.post(f"{API_BASE_URL}/edit-task", json=payload)
        resp.raise_for_status()
        resp = resp.json()

        if resp.get("error"):
            raise Exception(f"Failed to edit task: {resp['message']}")

    async def stop_task(self, task_id: int):
        resp = await self.session.post(f"{API_BASE_URL}/stop-task", json={"id": task_id})
        resp = resp.json()

        if resp.get("error"):
            raise Exception(f"Failed to stop task: {resp['message']}")

    async def delete_task(self, task_id: int):
        resp = await self.session.post(f"{API_BASE_URL}/delete-task", json={"id": task_id})
        resp = resp.json()

        if resp.get("error"):
            raise Exception(f"Failed to delete task: {resp['message']}")
