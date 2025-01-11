import asyncio
from main import TweetCatcher, CreateTaskArgs, PingRegex, PingKeywords
import traceback

tweet_catcher = TweetCatcher("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3aG9wVXNlcklkIjoidXNlcl9QbDhWdHFnbldRSG1HIiwidHlwZSI6ImFwaS1rZXkiLCJpYXQiOjE3MzY1NTIyNzF9.z1zWeHYs1rf7QrQlLNl7EoygN-uFx0FFVBZE1O8A804")


args = CreateTaskArgs(
    username="elonmusk",
    options=["posts", "retweets"],
    notification="discord",
    webhook="https://discord.com/api/webhooks/1316581166350077982/b7kWWJPEoeqUBZdcEIswK_2aYWrZQ871JWy5YgwAd4S4hEMsp6pX9OyNuF1XaI4qrctF",
    ping="none",
    pingKeywords=PingKeywords(positive=["Tesla", "SpaceX"], negative=["delay", "issue"]),
    start=True
)

async def create_task():
    response = await tweet_catcher.create_task(args)
    print("Task created successfully:", response)

if __name__ == "__main__":
    asyncio.run(create_task())