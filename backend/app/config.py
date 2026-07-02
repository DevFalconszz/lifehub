from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = 'LifeHub'
    app_version: str = '0.1.0'
    debug: bool = False

    supabase_url: str = 'https://pgqwjooucborcdqwsoui.supabase.co'
    supabase_anon_key: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBncXdqb291Y2JvcmNkcXdzb3VpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI5MjYyNzksImV4cCI6MjA5ODUwMjI3OX0.-rkqwEcXgQm10Lwt_dtNVFVlj9fzXctmvmYnCLvZ2dg'
    supabase_service_key: str = ''

    secret_key: str = 'change-me-in-production-lifehub-secret-key'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60 * 24

    cors_origins: list[str] = [
        'http://localhost:5173',
        'http://localhost:3000',
        'https://lifehub-frontend.vercel.app',
        'https://lifehub-frontend-git-main-sua-conta.vercel.app',
    ]

    model_config = {'env_file': '.env', 'env_file_encoding': 'utf-8', 'extra': 'ignore'}


@lru_cache
def get_settings() -> Settings:
    return Settings()
