import asyncio

import openai
from llmio.agent import Agent


agent = Agent(
    instruction="""
        You are a calculating agent running in Azure.
        """,
    client=openai.AsyncAzureOpenAI(
        api_key="<your-api-key",
        azure_endpoint="<your-azure-endpoint>",
        api_version="<your-api-version>",
    ),
    model="<your-deployment>",
)


@agent.tool
def add(num1: float, num2: float) -> float:
    print(f"** Adding: {num1} + {num2}")
    return num1 + num2


@agent.tool
async def multiply(num1: float, num2: float) -> float:
    print(f"** Multiplying: {num1} * {num2}")
    return num1 * num2


@agent.on_message
async def print_message(message: str):
    print(f"** Posting message: '{message}'")


async def main():
    response = await agent.speak("Hi! how much is 1 + 1?")
    response = await agent.speak(
        "and how much is that times two?", history=response.history
    )


if __name__ == "__main__":
    asyncio.run(main())
