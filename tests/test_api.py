from fastapi.testclient import TestClient

from app.main import app


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
    assert "decisions" in data


def test_analyze_url_requires_url():
    response = client.post(
        "/api/analyze",
        json={},
    )

    assert response.status_code == 422