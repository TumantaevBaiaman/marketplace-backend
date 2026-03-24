from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="LOG__",
        extra="ignore",
    )

    level: str = Field(default="INFO")
    format: str = Field(default="json")  # json | text
    output: str = Field(default="stdout")  # stdout | file
    file_path: str = Field(default="logs/app.log")

    @property
    def log_config(self) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {"()": "pythonjsonlogger.jsonlogger.JsonFormatter"},
                "text": {"format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"},
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "formatter": self.format,
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"level": self.level, "handlers": ["stdout"]},
        }
