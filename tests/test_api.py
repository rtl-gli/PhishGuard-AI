from fastapi.testclient import TestClient

from app.main import app
from src.predict import HIGH_RISK_THRESHOLD


client = TestClient(app)


def test_analyze_url():
    response = client.post(
        "/api/analyze",
        json={"url": "https://www.google.com"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "risk_level" in data
    assert "phishing_probability" in data
    assert "prediction" in data
    assert "indicators" in data
    assert "features" in data
    assert "explanations" in data
    assert data["explanations"]


def test_complex_legitimate_dashboard_url_is_not_high_risk():
    response = client.post(
        "/api/analyze",
        json={
            "url": (
                "https://dashboard.fastapicloud.com/"
                "tenant-1234/apps/sample-app/deployments"
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "MEDIUM"
    assert data["phishing_probability"] < HIGH_RISK_THRESHOLD
    assert "Deep URL path" in data["indicators"]


def test_analyze_url_requires_url():
    response = client.post(
        "/api/analyze",
        json={},
    )

    assert response.status_code == 422


def test_analyze_url_rejects_blank_url():
    response = client.post(
        "/api/analyze",
        json={"url": "   "},
    )

    assert response.status_code == 422
    assert "non-empty" in response.json()["detail"]


def test_analyze_url_rejects_invalid_url():
    response = client.post(
        "/api/analyze",
        json={"url": "not a valid url"},
    )

    assert response.status_code == 422
    assert "valid URL" in response.json()["detail"]


def test_analyze_url_rejects_single_label_hostname():
    response = client.post(
        "/api/analyze",
        json={"url": "not-a-url"},
    )

    assert response.status_code == 422
    assert "valid URL" in response.json()["detail"]


def test_analyze_url_rejects_excessively_long_url():
    response = client.post(
        "/api/analyze",
        json={"url": "https://example.com/" + "a" * 2048},
    )

    assert response.status_code == 422
    assert "2,048" in response.json()["detail"]