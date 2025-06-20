from fastapi import APIRouter, HTTPException, status

from graymatter.tools import BaseRegistry

from .schema import ChatRequest, GenerationResponse
from .service import OpenAIClient

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def completion(request: ChatRequest) -> GenerationResponse:
    try:
        client = OpenAIClient(request.model, BaseRegistry())
        if request.stream:
            return client.stream(
                messages=[
                    {"role": "system", "content": "You're a helpful assistant"},
                    {"role": "user", "content": request.query},
                ],
                temperature=request.temperature,
                top_p=request.top_p,
                tools=request.tools,
            )
        else:
            return client.complete(
                messages=[
                    {"role": "system", "content": "You're a helpful assistant"},
                    {"role": "user", "content": request.query},
                ],
                temperature=request.temperature,
                top_p=request.top_p,
                tools=request.tools,
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
