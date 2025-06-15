import os

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from .schema import GenerationResponse


class OpenAIClient:
    def __init__(self, model: str = "gpt-4.1") -> None:
        self.__api_key: str = os.environ["OPENAI_API_KEY"]
        self.client: OpenAI = OpenAI(api_key=self.__api_key)
        self.model = model

    def complete(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float,
        top_p: float,
    ) -> GenerationResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            stream=False,
        )

        if response.choices[0].message.tool_calls:
            raise NotImplementedError("Tool calls are not available")

        return GenerationResponse(
            content=response.choices[0].message.content,
            usage={
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            tool_calls=response.choices[0].message.tool_calls,
        )

    def stream(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float,
        top_p: float,
    ) -> GenerationResponse:
        stream_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            stream=True,
            stream_options={"include_usage": True},
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
