import json
from dataclasses import dataclass
from datetime import datetime

import openai

from llmio import Agent

from tests.utils import mocked_async_openai_replies
from openai.types.chat.chat_completion_message import (
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
)
from openai.types.chat.chat_completion_message_tool_call import Function


async def test_context() -> None:
    agent = Agent(
        instruction=f"You are a personal agent. You can help users set reminders. The current time is {datetime.now()}",
        client=openai.AsyncOpenAI(api_key="abc"),
        model="gpt-4o-mini",
    )

    @dataclass
    class User:
        id: str
        name: str

    @agent.tool()
    async def set_reminder(
        description: str, datetime_iso: datetime, _context: User
    ) -> str:
        return f"Successfully created reminder for user {_context.id}: {description} at {datetime_iso}"

    mocks = [
        ChatCompletionMessage.construct(
            content="Ok! Adding a reminder.",
            tool_calls=[
                ChatCompletionMessageToolCall.construct(
                    id="set_reminder_1",
                    type="function",
                    function=Function.construct(
                        name="set_reminder",
                        arguments=json.dumps(
                            {
                                "description": "A reminder",
                                "datetime_iso": "2022-01-01T00:00:00",
                            }
                        ),
                    ),
                ),
            ],
            role="assistant",
        ),
        ChatCompletionMessage.construct(
            role="assistant",
            content="I successfully created a reminder!",
        ),
    ]

    user = User(id="1", name="Alice")
    with mocked_async_openai_replies(mocks):
        response = await agent.speak("Set a reminder for me", _context=user)
    assert response.messages == [mocks[0].content, mocks[1].content]
    assert response.history == [
        {
            "role": "user",
            "content": "Set a reminder for me",
        },
        agent._parse_completion(mocks[0]),
        {
            "role": "tool",
            "tool_call_id": "set_reminder_1",
            "content": "Successfully created reminder for user 1: A reminder at 2022-01-01 00:00:00",
        },
        agent._parse_completion(mocks[1]),
    ]
