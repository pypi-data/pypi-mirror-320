import logging
from typing import Any

from .common import LoggerName, Timer

__all__ = ["DEBUG", "INFO", "WARN", "ERROR", "Timer"]


def DEBUG(msg: str, *args: Any, **kwargs: Any) -> None:
    logging.getLogger(LoggerName.get()).debug(msg, stacklevel=2, *args, **kwargs)


def INFO(msg: str, *args: Any, **kwargs: Any) -> None:
    logging.getLogger(LoggerName.get()).info(msg, stacklevel=2, *args, **kwargs)


def WARN(msg: str, *args: Any, **kwargs: Any) -> None:
    logging.getLogger(LoggerName.get()).warn(msg, stacklevel=2, *args, **kwargs)


def ERROR(msg: str, *args: Any, **kwargs: Any) -> None:
    logging.getLogger(LoggerName.get()).error(msg, stacklevel=2, *args, **kwargs)
