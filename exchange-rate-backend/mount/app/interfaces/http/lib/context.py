from starlette.requests import Request

from app.commons.database import DBSession
from app.commons.cache import CacheSession


class RequestContext:
    def __init__(self, request: Request):
        self._request = request

    @property
    def db(self) -> DBSession:
        return self._request.state.db

    @property
    def cache(self) -> CacheSession:
        return self._request.state.cache_session
