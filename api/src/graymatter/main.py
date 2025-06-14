from fastapi import FastAPI

from .api import api

app = FastAPI()
app.include_router(api)


@app.get("/health")
def check_health() -> dict[str, str]:
    return {"status": "ok"}
