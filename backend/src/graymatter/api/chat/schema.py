from uuid import UUID, uuid4

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


class Usage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, str]


class GenerationResponse(BaseModel):
    content: str | None
    usage: Usage
    tool_calls: list[ToolCall] | None
