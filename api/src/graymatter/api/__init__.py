from fastapi import APIRouter
from .chat import router as chat

api = APIRouter()
api.include_router(chat)

__all__ = ["api"]