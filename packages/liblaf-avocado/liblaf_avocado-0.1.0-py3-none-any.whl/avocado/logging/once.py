import functools

from loguru import logger


@functools.cache
def log_once(level: int | str, message: str, *args, depth: int = 1, **kwargs) -> None:
    logger.opt(depth=depth).log(level, message, *args, **kwargs)


trace_once = functools.partial(log_once, level="TRACE")
debug_once = functools.partial(log_once, level="DEBUG")
info_once = functools.partial(log_once, level="INFO")
success_once = functools.partial(log_once, level="SUCCESS")
warning_once = functools.partial(log_once, level="WARNING")
error_once = functools.partial(log_once, level="ERROR")
critical_once = functools.partial(log_once, level="CRITICAL")
