import pytest
from databases import Database
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import create_autospec

from app.commons.cache import CacheConnector, CacheSession
from app.commons.database import DBSession, DBConnector
from app.interfaces.http import (init_routes, init_event_handlers,
                                 init_error_handling, init_middleware)
from app.interfaces.http.lib.context import RequestContext


@pytest.fixture
@pytest.mark.asyncio
async def db_session() -> DBSession:
    db = create_autospec(DBSession)
    return db


@pytest.fixture
@pytest.mark.asyncio
async def cache_connector() -> CacheConnector:
    cache = create_autospec(CacheConnector)
    await cache.connect()
    return cache


@pytest.fixture
@pytest.mark.asyncio
async def cache_session() -> CacheSession:
    cache = create_autospec(CacheSession)
    return cache


@pytest.fixture
async def db_connector():
    db = create_autospec(DBConnector)
    db.read_db = create_autospec(Database)
    db.write_db = create_autospec(Database)
    await db.connect()
    return db


@pytest.fixture
def mock_context(db_session, cache_session):
    context = create_autospec(RequestContext)
    context.db = db_session
    context.cache = cache_session
    return context


@pytest.fixture
def app(db_connector, cache_connector):
    rest_api = FastAPI(
        title="Exchage Rate Service REST api",
        description="",
        docs_url="/docs",
    )
    rest_api.db_connector = db_connector
    rest_api.cache_connector = cache_connector
    init_routes(rest_api)
    init_error_handling(rest_api)
    init_middleware(rest_api)
    init_event_handlers(rest_api)

    return rest_api


@pytest.fixture
def app_client(app):
    client = TestClient(app, raise_server_exceptions=False)
    return client


@pytest.fixture
def mock_rates():
    return {
        "USD": 1,
        "AED": 3.67,
        "AFN": 103.85,
        "ALL": 107.84
    }
