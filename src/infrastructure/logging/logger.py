import logging


def get_logger(name: str) -> logging.Logger:
    """
    Фабрика логгеров. Каждый модуль получает именованный логгер:
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
