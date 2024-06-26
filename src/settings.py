from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    api_key: str
    task_url: str
    openai_api_key: str
    qdrant_url: str
    own_api_url: str
    renderform_api_key: str
    serp_api_key: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()
