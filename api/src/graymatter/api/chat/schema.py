from uuid import UUID, uuid4

from openai.types import CompletionUsage
from openai.types.chat import ChatCompletionMessageToolCall
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str
    conversation_id: UUID = Field(default=uuid4())
    model: str
    temperature: float = 0.8
    top_p: float = 1.0
    stream: bool = False
    tools: list[str] = []


class ChatResponse(BaseModel):
    response: str


class ChatCompletionToolCall(BaseModel):
    function_name: str
    arguments: str


class GenerationResponse(BaseModel):
    content: str | None
    usage: CompletionUsage
    tool_calls: list[ChatCompletionMessageToolCall | ChatCompletionToolCall] | None
