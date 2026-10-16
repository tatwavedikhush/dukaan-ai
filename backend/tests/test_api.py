import os

os.environ["MOCK_AI"] = "true"

from fastapi.testclient import TestClient

from backend.database import Base, engine
from backend.main import app


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_shop_product_and_extract_flow() -> None:
    with TestClient(app) as client:
        shop = client.post("/api/shops", json={"name": "Demo Mart", "whatsapp_number": "+911234567890"})
        assert shop.status_code == 201
        slug = shop.json()["slug"]
        draft = client.post(
            f"/api/shops/{slug}/extract",
            files={"images": ("tea.png", b"png", "image/png")},
            data={"text": "tea"},
        )
        assert draft.status_code == 200
        assert draft.json()[0]["name"] == "Masala Tea"
        assert client.get(f"/api/shops/{slug}").json()["products"] == []
        saved = client.post(f"/api/shops/{slug}/products", json={"products": draft.json()})
        assert saved.status_code == 201
        product_id = saved.json()[0]["id"]
        assert client.put(f"/api/shops/{slug}/products/{product_id}", json={"name": "Tea", "price": 10, "stock": 2}).status_code == 200
        assert client.delete(f"/api/shops/{slug}/products/{product_id}").status_code == 204


def test_extract_validation_and_unknown_shop() -> None:
    with TestClient(app) as client:
        assert client.get("/api/shops/missing").status_code == 404
        assert client.post("/api/shops/missing/extract", files={"images": ("x.txt", b"x", "text/plain")}).status_code == 404
        shop = client.post("/api/shops", json={"name": "Validation Shop", "whatsapp_number": "1"}).json()
        response = client.post(f"/api/shops/{shop['slug']}/extract", files={"images": ("x.txt", b"x", "text/plain")})
        assert response.status_code == 415
