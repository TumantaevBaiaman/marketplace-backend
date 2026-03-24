from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MINIO__",
        extra="ignore",
    )

    endpoint: str = Field(default="localhost:9000")
    public_endpoint: str = Field(
        default=""
    )  # публичный хост для браузера; если пусто — используется endpoint
    access_key: str = Field(default="minioadmin")
    secret_key: str = Field(default="minioadmin")
    secure: bool = Field(default=False)
    bucket: str = Field(default="marketplace")

    @property
    def endpoint_url(self) -> str:
        scheme = "https" if self.secure else "http"
        return f"{scheme}://{self.endpoint}"
