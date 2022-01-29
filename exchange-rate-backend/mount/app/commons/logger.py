import logging
from typing import Any

import structlog

from app.commons.settings import settings

# Log setup
IS_CONFIGURED = False


def _log_as_txt() -> bool:
    return settings.APP_ENV == "local" or settings.APP_ENV == "test"


def _setup() -> None:
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    _configure_std_logging(shared_processors)
    _configure_internal_logging(shared_processors)


def _configure_std_logging(shared_processors: list[Any]) -> None:
    if _log_as_txt():
        renderer = structlog.dev.ConsoleRenderer(colors=False)
    else:
        renderer = structlog.processors.JSONRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer, foreign_pre_chain=shared_processors
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)


def _configure_internal_logging(shared_processors: list[Any]) -> None:
    procs = [
        # _add_request_id_processor,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]
    structlog.configure(
        processors=shared_processors + procs,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# Logger operations
def get_logger() -> Any:
    global IS_CONFIGURED  # pylint: disable=global-statement
    if not IS_CONFIGURED:
        _setup()
        IS_CONFIGURED = True

    return structlog.wrap_logger(logging.getLogger())


def debug(*args, **kwargs) -> Any:
    return get_logger().debug(*args, **kwargs)


def info(*args, **kwargs) -> Any:
    return get_logger().info(*args, **kwargs)


def warning(*args, **kwargs) -> Any:
    return get_logger().warning(*args, **kwargs)


def critical(*args, **kwargs) -> Any:
    return get_logger().critical(*args, **kwargs)


def exception(*args, **kwargs) -> Any:
    return get_logger().exception(*args, **kwargs)


def error(*args, **kwargs) -> Any:
    return get_logger().error(*args, **kwargs)
