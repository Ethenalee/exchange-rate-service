"""init file for api service"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

import uvicorn
from starlette.staticfiles import StaticFiles
from starlette.requests import Request

from app.commons import logger, metrics, cache
from app.commons.database import new_connection_pool
from app.commons.exceptions import AppError
from app.commons.settings import settings
from app.interfaces.http.lib.responses import (ValidationErrorResponse,
                                               ErrorResponse)
from app.interfaces.http.lib.middlewares import (MetricsMiddleware,
                                                 DBSessionMiddleware,
                                                 CacheSessionMiddleware)


class HttpException(Exception):
    code: str
    http_status: int


def init_routes(app):
    if settings.APP_ENV == "local" or settings.APP_ENV == "test":
        logger.info("Serving test coverage reports at /tests")
        app.mount(
            "/tests",
            app=StaticFiles(
                directory="/srv/root/tests/htmlcov/", html=True,
                check_dir=False
            ),
        )

    from . import v1
    app.include_router(v1.router, prefix="/v1")
    from . import monitoring

    app.include_router(monitoring.router)


def init_error_handling(app):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, error: RequestValidationError
    ):
        logger.warning("RequestValidationError", error=error, exc_info=error)
        response = ValidationErrorResponse.from_exception(error)
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request,
                                error: AppError) -> ErrorResponse:
        logger.warning("AppError", error=str(error), exc_info=error)
        response = ErrorResponse.from_exception(error, status_code=424)
        return response

    @app.exception_handler(Exception)
    async def uncaught_error_handler(
        request: Request, error: Exception
    ) -> ErrorResponse:
        logger.warning("Unhandled Exception", error=str(error), exc_info=error)
        response = ErrorResponse(
            code="internal_server_error", message=str(error), status_code=500
        )
        return response


def init_middleware(app):
    app.add_middleware(MetricsMiddleware, metrics=metrics.Metrics())
    app.add_middleware(DBSessionMiddleware)
    app.add_middleware(CacheSessionMiddleware)


def init_event_handlers(app):
    @app.on_event("startup")
    async def open_database_connection_pool():
        logger.debug("opening db connection pool")
        db_pool = new_connection_pool()
        app.db_connector = db_pool
        await db_pool.connect()

    @app.on_event("startup")
    async def open_cache_connection_pool() -> None:
        app.cache_connector = cache.CacheConnector(
            settings.REDIS_DSN
        )
        await app.cache_connector.connect()


def init_api():
    logger.info("rest-api initializing")
    rest_api = FastAPI(
        title="Exchange Rate Service REST api",
        description="",
        docs_url="/docs",
    )
    init_routes(rest_api)
    init_error_handling(rest_api)
    init_middleware(rest_api)
    init_event_handlers(rest_api)

    uvicorn.run(
        rest_api,
        host="0.0.0.0",
        port=settings.SERVER_PORT,
    )
