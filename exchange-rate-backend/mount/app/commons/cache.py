from typing import Union

from aioredis import create_redis_pool, ConnectionsPool


class CacheException(Exception):
    pass


class CacheConnectionException(CacheException):
    pass


class CacheConnector:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._pool = None

    async def connect(self):
        if self._pool:
            return

        self._pool = await create_redis_pool(self.dsn)

    @property
    def pool(self) -> ConnectionsPool:
        if not self._pool:
            raise CacheConnectionException("Not connected")
        return self._pool

    async def close(self):
        self._pool.close()
        await self._pool.wait_closed()


class CacheSession:
    def __init__(self, connector: CacheConnector):
        self._connector = connector

    async def get(self, key: str) -> Union[str, None]:
        value = await self._connector.pool.get(key)

        return value.decode("utf-8") if value is not None else value

    async def set(self, key: str, value: str) -> bool:
        return await self._connector.pool.set(key, value)

    async def check_health(self) -> bool:
        response = await self._connector.pool.ping()
        return response == b"PONG"
