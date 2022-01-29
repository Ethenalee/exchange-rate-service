from starlette.requests import Request

from .context import RequestContext


def no_auth(request: Request) -> RequestContext:
    return RequestContext(request)
