# TweetCatcherPy

TweetCatcherPy is a Python wrapper for the Tweet Catcher API, providing an easy way to monitor Twitter activities such as posts, retweets, replies, and more. This library supports asynchronous operations and provides seamless integration with Discord, Telegram, Webhooks, and WebSocket notifications.

---

## Installation

To install TweetCatcherPy, simply add it to your project dependencies using `pip`:

```bash
pip install TweetCatcherPy
```

---

## Note
The Tweet Catcher Pro Plan is required to use this library.

Purchase at: https://whop.com/tweetcatcher

---

## Features

- Create tasks to monitor Twitter users.
- Receive notifications via Discord, Telegram, Webhooks, or WebSocket.
- Support for advanced filtering using positive/negative keywords or regular expressions.
- Manage tasks (start, edit, stop, delete).
- Retrieve user and task information.

---

## Getting Started

### Importing the Library

```python
from TweetCatcherPy import TweetCatcher, CreateTaskArgs, PingRegex, PingKeywords
```

### Authentication

To use the Tweet Catcher API, you need an API token. Initialize the `TweetCatcher` client with your token:

```python
api_token = "your_api_token_here"
tweet_catcher = TweetCatcher(api_token)
```

### Creating a Task

Define the parameters for the task using `CreateTaskArgs`. For example:

```python
from TweetCatcherPy import CreateTaskArgs, PingKeywords

args = CreateTaskArgs(
    username="elonmusk",
    options=["posts", "retweets"],
    notification="discord",
    webhook="https://discordapp.com/api/webhooks/...",
    ping="role",
    roleId="1234567890",
    pingKeywords=PingKeywords(positive=["Tesla", "SpaceX"], negative=["delay", "issue"]),
    start=True
)
```

Create the task:

```python
import asyncio

async def create_task():
    response = await tweet_catcher.create_task(args)
    print("Task created successfully:", response)

asyncio.run(create_task())
```

### Managing Tasks

#### Get All Tasks

```python
async def get_tasks():
    tasks = await tweet_catcher.get_tasks()
    print("Tasks:", tasks)

asyncio.run(get_tasks())
```

#### Start a Task

```python
async def start_task(task_id):
    response = await tweet_catcher.start_task(task_id)
    print("Task started successfully:", response)

asyncio.run(start_task(123))
```

#### Edit a Task

```python
async def edit_task(task_id):
    updated_args = CreateTaskArgs(
        username="elonmusk",
        options=["posts", "replies"],
        notification="telegram",
        chatId="@your_telegram_chat_id",
        start=False
    )

    response = await tweet_catcher.edit_task(task_id, updated_args)
    print("Task edited successfully:", response)

asyncio.run(edit_task(123))
```

#### Stop or Delete a Task

```python
async def stop_task(task_id):
    response = await tweet_catcher.stop_task(task_id)
    print("Task stopped successfully:", response)

async def delete_task(task_id):
    response = await tweet_catcher.delete_task(task_id)
    print("Task deleted successfully:", response)

asyncio.run(stop_task(123))
asyncio.run(delete_task(123))
```

### WebSocket Integration

Connect to the WebSocket to receive real-time updates:

```python
async def run_websocket():
    try:
        await tweet_catcher.start()
    
        while True:
            message = await tweet_catcher.get_message()
            print("New WebSocket Message:", message)
    
    except Exception as e:
        print("WebSocket Error:", e)
        
    finally:
        await tweet_catcher.stop()

asyncio.run(run_websocket())
```

---

## Error Handling

All API interactions raise exceptions if an error occurs. Make sure to handle them appropriately:

```python
try:
    response = await tweet_catcher.create_task(args)
except Exception as e:
    print("Error:", e)
```

## License

This project is licensed under a proprietary license. See the [LICENSE.md](https://github.com/lnstchtped/TweetCatcherPy/blob/master/LICENCE.md) file for details.

