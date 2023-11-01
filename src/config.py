from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_LOGIN: str
    SMTP_PASSWORD: str
    DB_URI: str
    model_config = SettingsConfigDict(env_file="src/.env")


settings = Settings(_env_file="src/.env")
