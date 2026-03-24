from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.database import DatabaseSettings
from src.config.jwt import JWTSettings
from src.config.logging import LoggingSettings
from src.config.minio import MinioSettings
from src.config.redis import RedisSettings


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    # App
    app_name: str = Field(default="Marketplace API")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)
    api_prefix: str = Field(default="/api")

    # CORS
    allowed_origins: list[str] = Field(default=["*"])
    allowed_methods: list[str] = Field(default=["*"])
    allowed_headers: list[str] = Field(default=["*"])

    # Nested configs
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    minio: MinioSettings = Field(default_factory=MinioSettings)

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
