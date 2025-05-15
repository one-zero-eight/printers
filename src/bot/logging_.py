__all__ = ["logger"]

import inspect
import logging.config
import os
from collections.abc import Mapping
from logging import LogRecord


class RelativePathFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.relativePath = os.path.relpath(record.pathname)
        return True


dictConfig = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "colorlog.ColoredFormatter",
            "format": "[%(black)s%(asctime)s%(reset)s] "
            "[%(log_color)s%(levelname)s%(reset)s] "
            "[%(name)s] %(message)s",
        },
        "src": {
            "()": "colorlog.ColoredFormatter",
            "format": "[%(black)s%(asctime)s%(reset)s] "
            "[%(log_color)s%(levelname)s%(reset)s] "
            '[%(cyan)sFile "%(relativePath)s", line '
            "%(lineno)d%(reset)s] %(message)s",
        },
    },
    "handlers": {
        "default": {"class": "logging.StreamHandler", "formatter": "default", "stream": "ext://sys.stdout"},
        "src": {"class": "logging.StreamHandler", "formatter": "src", "stream": "ext://sys.stdout"},
    },
    "loggers": {
        "aiogram": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "aiogram.event": {"level": "WARNING"},
        "src": {"handlers": ["src"], "level": "INFO", "propagate": False},
    },
}

logging.config.dictConfig(dictConfig)


class LoggerFromCaller(logging.Logger):
    def makeRecord(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: object,
        args,
        exc_info,
        func: str | None = None,
        extra: Mapping[str, object] | None = None,
        sinfo: str | None = None,
    ) -> LogRecord:
        record = super().makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)
        if extra is not None:
            step_back = extra.get("step_back", 0)
            if step_back:
                step_back: int
                frame = inspect.currentframe()
                for _ in range(step_back):
                    frame = frame.f_back
                record.relativePath = os.path.relpath(frame.f_code.co_filename)
                record.pathname = frame.f_code.co_filename
                record.lineno = frame.f_lineno
        return record


logger = logging.getLogger("src.bot")
logger.addFilter(RelativePathFilter())
logger.__class__ = LoggerFromCaller
