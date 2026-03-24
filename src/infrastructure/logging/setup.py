import logging
import logging.config

from src.config import get_settings

_configured = False


def configure_logging() -> None:
    """Вызывается один раз при старте приложения."""
    global _configured
    if _configured:
        return

    settings = get_settings().logging

    formatter: dict
    if settings.format == "json":
        formatter = {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
        }
    else:
        formatter = {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }

    handlers: dict = {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        }
    }

    if settings.output == "file":
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.file_path,
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "default",
        }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"default": formatter},
            "handlers": handlers,
            "root": {
                "level": settings.level,
                "handlers": list(handlers.keys()),
            },
            # снижаем шум от сторонних библиотек
            "loggers": {
                "uvicorn.access": {"level": "WARNING"},
                "sqlalchemy.engine": {"level": "WARNING"},
            },
        }
    )

    _configured = True
