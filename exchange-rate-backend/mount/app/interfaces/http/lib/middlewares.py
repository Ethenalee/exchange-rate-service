import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
from starlette.requests import Request

from app.commons.metrics import Metrics
from app.commons.settings import settings
from app.commons.database import DBSession
from app.commons.cache import CacheSession


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, metrics: Metrics, **kwargs):
        self.metrics = metrics
        super().__init__(app, **kwargs)

    @staticmethod
    def find_route(router, scope):
        for route in router.routes:
            match, _ = route.matches(scope)
            if match != Match.NONE:
                return route.path
        else:
            return scope["path"]

    async def dispatch(self, request: Request, call_next):
        route = MetricsMiddleware.find_route(request.app.router, request.scope)
        request_start_time = time.time()

        response = await call_next(request)

        self.metrics.REQUEST_COUNT.labels(settings.APP_NAME, route,
                                          settings.APP_ENV).inc()
        total_seconds = time.time() - request_start_time
        self.metrics.REQUEST_LATENCY.labels(
            settings.APP_NAME, route, settings.APP_ENV).set(total_seconds)

        return response


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db_session = DBSession(request.app.db_connector)
        request.state.db = db_session
        return await call_next(request)


class CacheSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        cache_session = CacheSession(request.app.cache_connector)
        request.state.cache_session = cache_session
        return await call_next(request)
