from typing import Awaitable, Callable

import asyncio

from . import logger
from .settings import settings

SLEEP_TIME = 5


class ConnectionRetriesExceededError(Exception):
    pass


async def retry_connection(
    retry_counter: int,
    initialize_connection: Callable[[int], Awaitable[None]],
    connection_name: str,
) -> None:
    if retry_counter < settings.CONNECTION_RETRIES:
        retry_counter += 1
        logger.warning(
            f"retrying connection in {SLEEP_TIME} seconds"
            f" - attempt {retry_counter} / {settings.CONNECTION_RETRIES}"
        )
        await asyncio.sleep(SLEEP_TIME)
        await initialize_connection(retry_counter)
    else:
        raise ConnectionRetriesExceededError(
            f"Retries exceeded for {connection_name} connection"
        )
