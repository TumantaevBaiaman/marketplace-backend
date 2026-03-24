from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB__",
        extra="ignore",
    )

    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="marketplace")
    user: str = Field(default="postgres")
    password: str = Field(default="postgres")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    pool_timeout: int = Field(default=30)
    echo: bool = Field(default=False)

    @computed_field
    @property
    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )
