import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TAVILY_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    setting = Settings()
    os.environ["TAVILY_API_KEY"] = setting.TAVILY_API_KEY
    return setting
