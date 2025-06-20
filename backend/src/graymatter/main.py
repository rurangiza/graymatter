from fastapi import FastAPI

from .api import api
from .config import get_settings

get_settings()

app = FastAPI()
app.include_router(api)


@app.get("/health")
def check_health() -> dict[str, str]:
    return {"status": "ok. Hello world."}
