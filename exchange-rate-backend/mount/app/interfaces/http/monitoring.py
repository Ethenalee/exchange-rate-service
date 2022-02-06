import prometheus_client

from fastapi import APIRouter, Security
from starlette.requests import Request
from starlette.responses import Response

from app.commons import logger
from app.commons.settings import settings
from app.commons.metrics import Metrics
from app.commons.database import do_db_health_check
from app.interfaces.http.lib.auth import no_auth
from app.interfaces.http.lib.context import RequestContext
from app.interfaces.http.lib.responses import failure, success

router = APIRouter()


class HealthCheckStatus:
    HEALTHY = 0
    MAIN_DEPENDENCY_ERROR = 1
    SUB_DEPENDENCY_ERROR = 2


@router.get("/health", tags=["Monitoring"])
async def health_check(ctx: RequestContext = Security(no_auth)):
    logger.info("health status")

    db_conncs_statuses = [
            await do_db_health_check(
                ctx.db.exec_read_one("SELECT version()"),
                "read",
            ),
            await do_db_health_check(
                ctx.db.exec_write("SELECT version()"),
                "write",
            ),
        ]
    db_health = all(db_conncs_statuses)

    if all(status for status in [db_health]):
        Metrics.HEALTH_CHECK.labels(
            app_name=settings.APP_NAME, dependency="All",
            environment=settings.APP_ENV
        ).set(HealthCheckStatus.HEALTHY)
    else:
        failed_dependencies = []

        if not db_health:
            failed_dependencies.append("db_health")

        if "db_health" in failed_dependencies:
            Metrics.HEALTH_CHECK._metrics.clear()
            Metrics.HEALTH_CHECK.labels(
                app_name=settings.APP_NAME,
                dependency=",".join(failed_dependencies),
                environment=settings.APP_ENV
            ).set(HealthCheckStatus.MAIN_DEPENDENCY_ERROR)
        else:
            Metrics.HEALTH_CHECK._metrics.clear()
            Metrics.HEALTH_CHECK.labels(
                app_name=settings.APP_NAME,
                dependency=",".join(failed_dependencies),
                environment=settings.APP_ENV
            ).set(HealthCheckStatus.SUB_DEPENDENCY_ERROR)

    if db_health:
        return success("Healthy", status_code=200)
    else:
        return failure("Unhealthy", status_code=500)


@router.get("/metrics", status_code=200, tags=["Monitoring"])
def metrics(request: Request) -> Response:
    logger.info("prometheus stats")
    return Response(
        prometheus_client.generate_latest(),
        media_type=prometheus_client.CONTENT_TYPE_LATEST,
    )
