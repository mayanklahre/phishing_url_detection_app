from fastapi.testclient import TestClient

from phishing_detector.api import create_app


def test_predict_and_healthz(loaded_model) -> None:
    with TestClient(create_app(model=loaded_model)) as client:
        health = client.get("/healthz")
        assert health.status_code == 200
        assert health.json()["model_version"] == "test-v1"
        response = client.post("/predict", json={"url": "https://example.com/login"})
    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "legitimate"
    assert body["model_version"] == "test-v1"
    assert body["latency_ms"] >= 0


def test_landing_page_is_available_without_changing_api_routes(loaded_model) -> None:
    with TestClient(create_app(model=loaded_model)) as client:
        response = client.get("/")
        health = client.get("/healthz")

    assert response.status_code == 200
    assert "LinkSentry" in response.text
    assert "fetch('/predict'" in response.text
    assert health.status_code == 200


def test_live_enrichment_rejects_loopback_before_request(loaded_model) -> None:
    with TestClient(create_app(model=loaded_model)) as client:
        response = client.post("/predict", json={"url": "http://127.0.0.1/", "include_live_features": True})
    assert response.status_code == 422
