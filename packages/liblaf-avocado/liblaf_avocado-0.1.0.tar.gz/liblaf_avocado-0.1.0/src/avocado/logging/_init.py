import logging
import sys

import rich.traceback
from loguru import logger

from ._handler import InterceptHandler

DEFAULT_FILTER: dict[str | None, str | int | bool] = {
    "everett": logging.INFO,
    "git.cmd": logging.INFO,
    "jax._src": logging.INFO,
    "numba.core": logging.INFO,
    "urllib3.connectionpool": logging.INFO,
}


def init_logging(level: str | int = logging.NOTSET) -> None:
    rich.traceback.install(show_locals=True)
    logger.remove()
    logger.add(sys.stderr, level=level, filter=DEFAULT_FILTER)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
