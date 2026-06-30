from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = 'LifeHub'
    app_version: str = '0.1.0'
    debug: bool = True

    database_url: str = 'postgresql+asyncpg://lifehub:lifehub@localhost:5433/lifehub'
    database_url_sync: str = 'postgresql://lifehub:lifehub@localhost:5433/lifehub'

    redis_url: str = 'redis://localhost:6379/1'

    secret_key: str = 'change-me-in-production-lifehub-secret-key'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60 * 24

    cors_origins: list[str] = ['http://localhost:5173', 'http://localhost:3000']

    model_config = {'env_file': '.env', 'env_file_encoding': 'utf-8'}


@lru_cache
def get_settings() -> Settings:
    return Settings()
