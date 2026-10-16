from fastapi.testclient import TestClient

from backend.ai import MockExtractor, parse_price
from backend.main import app


def test_health_endpoint_and_mock_extractor() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    biscuits = MockExtractor().extract([], "biscuits")
    soaps = MockExtractor().extract([], "soap")
    assert biscuits != soaps
    assert parse_price("Rs 499") == 499
    assert parse_price("₹499/-") == 499
    assert parse_price("four ninety nine") == 499
