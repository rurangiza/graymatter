import os

from openai import OpenAI

from .schema import GenerationResponse


class OpenAIClient:
    def __init__(self, model: str = "gpt-4.1") -> None:
        self.__api_key: str = os.environ["OPENAI_API_KEY"]
        self.client: OpenAI = OpenAI(api_key=self.__api_key)
        self.model = model

    def complete(
        self, messages: list[dict], temperature: float, top_p: float
    ) -> GenerationResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            stream=False,
        )
        return GenerationResponse(
            content=response.choices[0].message.content,
            usage=response.usage,
            tool_calls=response.choices[0].message.tool_calls,
        )
