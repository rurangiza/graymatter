from fastapi import APIRouter

from .schema import ChatRequest, GenerationResponse
from .service import OpenAIClient

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def completion(request: ChatRequest) -> GenerationResponse:
    client = OpenAIClient(request.model)
    if request.stream:
        return client.stream(
            messages=[
                {"role": "system", "content": "You're a helpful assistant"},
                {"role": "user", "content": request.query},
            ],
            temperature=request.temperature,
            top_p=request.top_p,
        )
    else:
        return client.complete(
            messages=[
                {"role": "system", "content": "You're a helpful assistant"},
                {"role": "user", "content": request.query},
            ],
            temperature=request.temperature,
            top_p=request.top_p,
        )
