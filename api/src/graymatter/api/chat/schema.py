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


class ChatResponse(BaseModel):
    response: str


class GenerationResponse(BaseModel):
    content: str | None
    usage: CompletionUsage
    tool_calls: ChatCompletionMessageToolCall | None
