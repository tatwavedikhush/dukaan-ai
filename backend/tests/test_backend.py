from fastapi.testclient import TestClient

from sqlalchemy import inspect, select

from backend.ai import MockExtractor, parse_price
from backend.database import SessionLocal, engine
from backend.main import app, initialize_database
from backend.models import Shop


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


def test_demo_seed_is_idempotent_and_repairs_product_image_column() -> None:
    initialize_database()
    initialize_database()
    with SessionLocal() as db:
        shop = db.scalar(select(Shop).where(Shop.slug == "demo-boutique"))
        assert shop is not None
        assert len(shop.products) == 7
        assert all(product.image_url and product.image_url.startswith("/uploads/") for product in shop.products)
    assert "image_url" in {column["name"] for column in inspect(engine).get_columns("products")}


def test_mock_extractor_recognizes_session_four_examples() -> None:
    extractor = MockExtractor()
    kurta = extractor.extract([], "red kurta 499")
    jeans = extractor.extract([], "blue jeans Rs 899 sizes 30 32")
    namkeen = extractor.extract([], "2 packs namkeen 120 each")
    assert kurta[0]["price"] == 499 and "red" in kurta[0]["name"].lower()
    assert jeans[0]["price"] == 899 and jeans[0]["variants"] == ["30", "32"]
    assert namkeen[0]["price"] == 120 and namkeen[0]["stock"] == 2
