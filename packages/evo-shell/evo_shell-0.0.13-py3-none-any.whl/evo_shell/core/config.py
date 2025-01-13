import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    REDIS_HOST: str = os.getenv("REDIS_HOST", "")
    REDIS_PORT: int = os.getenv("REDIS_PORT", "")
    REDIS_DB: int = os.getenv("REDIS_DB")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    CLICKHOUSE_HOST: str = os.getenv("CLICKHOUSE_HOST", "")
    CLICKHOUSE_PORT: str = os.getenv("CLICKHOUSE_PORT", "")
    CLICKHOUSE_USERNAME: str = os.getenv("CLICKHOUSE_USERNAME", "")
    CLICKHOUSE_PASSWORD: str = os.getenv("CLICKHOUSE_PASSWORD", "")

    class Config:
        case_sensitive = True


settings = Settings()
