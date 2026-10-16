import os
from pathlib import Path

os.environ["MOCK_AI"] = "true"

from fastapi.testclient import TestClient

from backend.database import Base, engine
from backend.main import app
from backend.main import UPLOADS_DIR


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


def test_extraction_image_is_persisted_and_served() -> None:
    with TestClient(app) as client:
        shop = client.post("/api/shops", json={"name": "Images", "whatsapp_number": "1"}).json()
        response = client.post(
            f"/api/shops/{shop['slug']}/extract",
            files={"images": ("unsafe name.png", b"png-data", "image/png")},
        )
        assert response.status_code == 200
        image_url = response.json()[0]["image_url"]
        assert image_url.startswith("/uploads/")
        assert Path(UPLOADS_DIR / image_url.removeprefix("/uploads/")).read_bytes() == b"png-data"
        served = client.get(image_url)
        assert served.status_code == 200
        assert served.content == b"png-data"


def test_product_image_url_accepts_uploaded_reference_and_rejects_traversal() -> None:
    with TestClient(app) as client:
        shop = client.post("/api/shops", json={"name": "Product Images", "whatsapp_number": "1"}).json()
        payload = {"products": [{"name": "Tea", "price": 10, "image_url": "/uploads/a.png"}]}
        saved = client.post(f"/api/shops/{shop['slug']}/products", json=payload)
        assert saved.status_code == 201
        assert saved.json()[0]["image_url"] == "/uploads/a.png"
        invalid = {"products": [{"name": "Tea", "price": 10, "image_url": "/uploads/../secret"}]}
        assert client.post(f"/api/shops/{shop['slug']}/products", json=invalid).status_code == 422
