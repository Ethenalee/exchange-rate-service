def test_get_metrics_returns_200_ok(app_client):
    resp = app_client.get("/metrics")
    assert resp.status_code == 200


def test_get_health_returns_200_ok(app_client):
    resp = app_client.get("/health")
    assert resp.status_code == 200
