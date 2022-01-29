from prometheus_client import Counter, Gauge


class Metrics:
    REQUEST_COUNT = Counter(
        "request_count", "App Request Count",
        ["app_name", "route", "environment"]
    )

    REQUEST_LATENCY = Gauge(
        "request_latency_seconds",
        "Request latency",
        ["app_name", "route", "environment"],
    )

    HEALTH_CHECK = Gauge(
        "health_checks",
        "Error code based on dependencies' health",
        ["app_name", "dependency", "environment"],
    )
