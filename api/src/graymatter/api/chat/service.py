import json
import os
from abc import ABC, abstractmethod

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)
from openai.types.chat import ChatCompletionMessageToolCall as ToolCallMessage

from graymatter.api.chat.exceptions import CompletionError
from graymatter.tools import ToolRegistry

from .schema import GenerationResponse
from .utils import Usage


class LLMClient(ABC):
    tool_registry: ToolRegistry = None

    @abstractmethod
    def complete(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float,
        top_p: float,
        tools: list[ChatCompletionToolParam] | None = None,
    ) -> GenerationResponse:
        pass

    @abstractmethod
    def stream(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float,
        top_p: float,
        tools: list[ChatCompletionToolParam] | None = None,
    ) -> GenerationResponse:
        pass

    def execute_tools(
        self, tool_calls: list[ToolCallMessage]
    ) -> list[ChatCompletionToolMessageParam]:
        messages = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            ChosenTool = self.tool_registry.get_tool_by_name(function_name)
            result = ChosenTool(**args).resolve()
            messages.append(
                ChatCompletionToolMessageParam(
                    content=result, role="tool", tool_call_id=tool_call.id
                )
            )
        return messages


class OpenAIClient(LLMClient):
    def __init__(self, model: str, tool_registry: ToolRegistry) -> None:
        self.__api_key: str = os.environ["OPENAI_API_KEY"]
        self.client: OpenAI = OpenAI(api_key=self.__api_key)
        self.model = model
        self.usage = Usage()
        self.tool_registry = tool_registry

    def complete(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float,
        top_p: float,
        tools: list[str] | None = [],
    ) -> GenerationResponse:
        try:
            tool_definitions = self.tool_registry.get_tool_definitions_by_names(tools)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                stream=False,
                tool_choice="auto" if tool_definitions else None,
                tools=tool_definitions,
            )
            self.usage += response.usage

            if tool_calls := response.choices[0].message.tool_calls:
                messages.append(
                    ChatCompletionAssistantMessageParam(
                        content=None, role="assistant", tool_calls=tool_calls
                    )
                )
                messages.extend(self.execute_tools(tool_calls))
                return self.complete(
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                )

            return GenerationResponse(
                content=response.choices[0].message.content,
                usage={
                    "completion_tokens": self.usage.completion_tokens,
                    "prompt_tokens": self.usage.prompt_tokens,
                    "total_tokens": self.usage.total_tokens,
                },
                tool_calls=response.choices[0].message.tool_calls,
            )
        except Exception as e:
            raise CompletionError(e)

    def stream(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float,
        top_p: float,
        tools: list[ChatCompletionToolParam] | None = None,
    ) -> GenerationResponse:
        stream_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            stream=True,
            stream_options={"include_usage": True},
            tool_choice="auto",
            tools=tools,
        )
        first_chunk = next(stream_response)

        full_content, usage = "", {}

        if first_chunk.choices[0].delta.tool_calls:
            raise NotImplementedError("Tool calls are not available")
        else:
            full_content += first_chunk.choices[0].delta.content

        for chunk in stream_response:
            if chunk.choices and (content := chunk.choices[0].delta.content):
                full_content += content
            elif completion_usage := chunk.usage:
                usage = completion_usage

        return GenerationResponse(
            content=full_content,
            usage={
                "completion_tokens": usage.completion_tokens,
                "prompt_tokens": usage.prompt_tokens,
                "total_tokens": usage.total_tokens,
            },
            tool_calls=None,
        )
