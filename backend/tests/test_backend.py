from fastapi.testclient import TestClient

from backend.extractors import MockExtractor
from backend.main import app


def test_health_endpoint_and_mock_extractor() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert MockExtractor().extract("name: Tea\nprice: 12") == {
        "name": "Tea",
        "price": "12",
    }
