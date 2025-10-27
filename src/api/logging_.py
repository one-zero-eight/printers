__all__ = ["logger"]

import asyncio
import inspect
import logging.config
import os
from typing import Any

import fastapi
from fastapi.dependencies.models import Dependant
from starlette.concurrency import run_in_threadpool


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
            "format": "[%(black)s%(asctime)s%(reset)s] [%(log_color)s%(levelname)s%(reset)s] [%(name)s] %(message)s",
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
        "src": {"handlers": ["src"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "httpx": {"handlers": ["default"], "level": "WARNING", "propagate": False},
    },
}

logging.config.dictConfig(dictConfig)

logger = logging.getLogger("src")
logger.addFilter(RelativePathFilter())


async def run_endpoint_function(*, dependant: Dependant, values: dict[str, Any], is_coroutine: bool) -> Any:
    # Only called by get_request_handler. Has been split into its own function to
    # facilitate profiling endpoints, since inner functions are harder to profile.
    assert dependant.call is not None, "dependant.call must be a function"
    loop = asyncio.get_running_loop()
    start_time = loop.time()
    if is_coroutine:
        r = await dependant.call(**values)
    else:
        r = await run_in_threadpool(dependant.call, **values)
    finish_time = loop.time()
    duration = finish_time - start_time
    callback = dependant.call
    func_name = callback.__name__
    pathname = inspect.getsourcefile(callback) or "unknown"
    lineno = inspect.getsourcelines(callback)[1]
    record = logging.LogRecord(
        name="src.fastapi.run_endpoint_function",
        level=logging.INFO,
        pathname=pathname,
        lineno=lineno,
        msg=f"Handler `{func_name}` took {int(duration * 1000)} ms",
        args=(),
        exc_info=None,
        func=func_name,
    )
    record.relativePath = os.path.relpath(record.pathname)
    logger.handle(record)
    return r


# monkey patch fastapi to log endpoint function duration and link to source code
fastapi.routing.run_endpoint_function = run_endpoint_function
