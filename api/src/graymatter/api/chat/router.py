from fastapi import APIRouter, HTTPException

from .schema import ChatRequest, GenerationResponse
from .service import OpenAIClient

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def generate_response(request: ChatRequest) -> GenerationResponse:
    client = OpenAIClient(request.model)
    if request.stream:
        raise HTTPException(status_code=400, detail="Streaming is not implemented yet")
    else:
        return client.complete(
            messages=[
                {"role": "system", "content": "You're a helpful assistant"},
                {"role": "user", "content": request.query},
            ],
            temperature=request.temperature,
            top_p=request.top_p,
        )
