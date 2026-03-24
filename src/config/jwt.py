from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="JWT__",
        extra="ignore",
    )

    secret_key: str = Field()  # обязателен — нет дефолта
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=30)
    token_type: str = Field(default="Bearer")
