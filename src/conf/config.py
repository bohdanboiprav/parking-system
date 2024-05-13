from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "postgresql+asyncpg://admin:$1234567@$name/$name"
    SECRET_KEY_JWT: str = "secret"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: str = "admin@meta.ua"
    MAIL_PASSWORD: str = "123456789"
    MAIL_FROM: str = "example@meta.ua"
    MAIL_PORT: int = 567234
    MAIL_SERVER: str = "example.meta.ua"
    MAIL_USE_SSL: bool = True
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLOUDINARY_NAME: str = "admin"
    CLOUDINARY_API_KEY: str = "a1221d111d1"
    CLOUDINARY_API_SECRET: str = "secret"
    APP_ENV: str = "dev"
    ADMIN_PASSWORD: str = "password"
    TELEGRAM_TOKEN: str = "6694067814:AAEL9ue1obl3_Zv5cCPcVhFKUt-qyqj9HDU"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


settings = Settings()
