import json
import os
from abc import ABC, abstractmethod

from openai import OpenAI, Stream
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)
from openai.types.chat import ChatCompletionMessageToolCall as ToolCallMessage

from graymatter.api.chat.exceptions import (
    CompletionError,
    StreamingError,
    UnexpectedFinishReason,
)
from graymatter.tools import ToolRegistry

from .schema import ChatCompletionToolCall, GenerationResponse
from .utils import Usage


class LLMClient(ABC):
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
        self.tool_registry = tool_registry

        self.usage = Usage()
        self.streamed_content: str = ""
        self.tool_calls: list[ChatCompletionMessageToolCall] = None

    def complete(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float,
        top_p: float,
        tools: list[str] = [],
    ) -> GenerationResponse:
        try:
            tool_definitions = self.tool_registry.get_tool_definitions_by_names(tools)

            response: ChatCompletion = self.client.chat.completions.create(
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
                self.tool_calls = tool_calls
                messages.append(
                    ChatCompletionAssistantMessageParam(
                        content=None, role="assistant", tool_calls=self.tool_calls
                    )
                )
                messages.extend(self.execute_tools(self.tool_calls))
                return self.complete(
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                )

            return GenerationResponse(
                content=response.choices[0].message.content,
                usage=self.usage.dict(),
                tool_calls=self.tool_calls,
            )
        except Exception as e:
            raise CompletionError(e)

    def stream(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float,
        top_p: float,
        tools: list[str] = [],
    ) -> GenerationResponse:
        try:
            tool_definitions = self.tool_registry.get_tool_definitions_by_names(tools)

            stream_response: Stream[ChatCompletionChunk] = (
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    stream=True,
                    stream_options={"include_usage": True},
                    tool_choice="auto" if tool_definitions else None,
                    tools=tool_definitions,
                )
            )

            _tool_calls: dict[int, ChatCompletionMessageToolCall] = {}
            _finish_reason: str = ""
            for chunk in stream_response:
                if choices := chunk.choices:
                    for tool_call in choices[0].delta.tool_calls or []:
                        index = tool_call.index
                        if index not in _tool_calls:
                            _tool_calls[index] = tool_call
                        _tool_calls[
                            index
                        ].function.arguments += tool_call.function.arguments
                    if content := choices[0].delta.content:
                        self.streamed_content += content
                    if finish_reason := choices[0].finish_reason:
                        # we don't exit because the usage chunk comes after finish_reason
                        _finish_reason = finish_reason
                if usage := chunk.usage:
                    self.usage += usage

            match _finish_reason:
                case "stop":
                    return GenerationResponse(
                        content=self.streamed_content,
                        usage=self.usage.dict(),
                        tool_calls=[
                            ChatCompletionToolCall(
                                function_name=tool_call.function.name,
                                arguments=tool_call.function.arguments,
                            )
                            for tool_call in self.tool_calls
                        ]
                        if self.tool_calls
                        else None,
                    )
                case "tool_calls":
                    self.tool_calls = list(_tool_calls.values())
                    messages.append(
                        ChatCompletionAssistantMessageParam(
                            content=None,
                            role="assistant",
                            tool_calls=self.tool_calls,
                        )
                    )
                    messages.extend(self.execute_tools(self.tool_calls))
                    return self.stream(messages, temperature, top_p)
                case _:
                    raise UnexpectedFinishReason(finish_reason)
        except Exception as e:
            raise StreamingError(str(e))
