import contextlib
import traceback
from typing import Any, Optional, Mapping

from databases import Database


from app.commons import logger
from app.commons.settings import settings
from app.commons.retry_connection import retry_connection


class DBError(Exception):
    pass


class DBConnectionError(DBError):
    pass


class DBExecutionError(DBError):
    pass


class DBConnector:
    def __init__(
        self,
        write_dsn: str,
        read_dsn: str,
        min_pool_size: int,
        max_pool_size: int,
        ssl: str,
    ) -> None:
        self.read_db = Database(
            read_dsn, ssl=ssl, min_size=min_pool_size, max_size=max_pool_size
        )
        self.write_db = Database(
            write_dsn, ssl=ssl, min_size=min_pool_size, max_size=max_pool_size
        )
        self._read_connection = None
        self._write_connection = None

    async def connect(self, retry_counter=0) -> None:
        if self._read_connection and self._write_connection:
            retry_counter = 0
            return

        try:
            logger.info("init db connection pools")
            await self.read_db.connect()
            await self.write_db.connect()
            self._read_connection = self.read_db.connection()
            self._write_connection = self.write_db.connection()

        except BaseException as error:
            logger.warning("db connection pools not started", error=error)

        if not self._read_connection or not self._write_connection:
            await retry_connection(retry_counter, self.connect, "db")

    async def close(self) -> None:
        logger.info("Closing connections")
        try:
            if self._read_connection is not None:
                await self.read_db.disconnect()

            if self._write_connection is not None:
                await self.read_db.disconnect()

        except Exception:
            raise


class DBSession:
    def __init__(self, connection: DBConnector) -> None:
        self._connection = connection

    @contextlib.asynccontextmanager
    async def transaction(self):
        async with self._connection.write_db.connection().transaction():
            yield

    async def exec_write(
        self, query: str, values: dict[str, Any] = None
    ) -> Optional[Mapping]:
        async with self._connection.write_db.connection() as connection:
            try:
                return await connection.fetch_one(query, values)
            except Exception as err:
                logger.exception(
                    "Db write error! ", query=query, values=values)
                logger.exception(traceback.format_exc())
                raise DBExecutionError() from err

    async def exec_read(
        self, query: str, values: Optional[dict[str, Any]] = None
    ) -> list[Mapping]:
        async with self._connection.read_db.connection() as connection:
            try:
                result = await connection.fetch_all(query, values)

            except Exception as err:
                logger.exception("db read error: ", query=query, values=values)
                logger.exception(traceback.format_exc())
                raise DBExecutionError() from err

            else:
                logger.debug(
                    "executing db read: ",
                    query=query,
                    values=values,
                    result=result,
                )
                return result

    async def exec_read_one(
        self, query: str, values: Optional[dict[str, Any]] = None
    ) -> Optional[Mapping]:
        async with self._connection.read_db.connection() as connection:
            try:
                result = await connection.fetch_one(query, values)

            except Exception as err:
                logger.exception("db read error: ", query=query, values=values)
                logger.exception(traceback.format_exc())
                raise DBExecutionError() from err

            else:
                logger.debug(
                    "executing db read: ",
                    query=query,
                    params=values,
                    result=result,
                )
                return result


def new_connection_pool() -> DBConnector:
    read_dsn = (
        f"postgresql://{settings.READ_DB_USER}:{settings.READ_DB_PASS}"
        f"@{settings.READ_DB_HOST}:{settings.READ_DB_PORT}/{settings.DB_NAME}"
    )

    write_dsn: str = (
        f"postgresql://{settings.WRITE_DB_USER}:{settings.WRITE_DB_PASS}"
        f"@{settings.WRITE_DB_HOST}"
        f":{settings.WRITE_DB_PORT}/{settings.DB_NAME}"
    )

    return DBConnector(
        write_dsn=write_dsn,
        read_dsn=read_dsn,
        min_pool_size=settings.DB_MIN_POOL_SIZE,
        max_pool_size=settings.DB_MAX_POOL_SIZE,
        ssl=settings.DB_SSL,
    )


async def do_db_health_check(db_operation, conn_name: str) -> bool:
    try:
        if await db_operation:
            return True
    except Exception as err:  # pragma: no cover
        logger.error(f"Unable to connect to {conn_name} database: {err}")
    return False
