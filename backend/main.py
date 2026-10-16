"""FastAPI application entry point and shop/product API."""

import re
import unicodedata
from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import ai
from .database import create_tables, get_db
from .models import Product, Shop

app = FastAPI(title="DukaanAI API")


class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    currency: str = Field(default="INR", max_length=8)
    description: str = ""
    category: str = Field(default="General", max_length=100)
    variants: list[str] = []


class ProductOut(ProductIn):
    id: int
    class Config:
        from_attributes = True


class ProductListIn(BaseModel):
    products: list[ProductIn]


class ProductDraft(ProductIn):
    """Validated extraction result that is not persisted."""


class ShopCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    whatsapp_number: str = Field(min_length=1, max_length=40)


class ShopOut(BaseModel):
    id: int
    name: str
    whatsapp_number: str
    slug: str
    products: list[ProductOut]
    class Config:
        from_attributes = True


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-") or "shop"


def find_shop(slug: str, db: Session) -> Shop:
    shop = db.scalar(select(Shop).where(Shop.slug == slug))
    if shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop


@app.on_event("startup")
def initialize_database() -> None:
    create_tables()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/shops", response_model=ShopOut, status_code=status.HTTP_201_CREATED)
def create_shop(payload: ShopCreate, db: Session = Depends(get_db)):
    base, n = slugify(payload.name), 0
    while db.scalar(select(Shop).where(Shop.slug == (base if n == 0 else f"{base}-{n}"))): n += 1
    shop = Shop(name=payload.name, whatsapp_number=payload.whatsapp_number, slug=base if n == 0 else f"{base}-{n}")
    db.add(shop); db.commit(); db.refresh(shop)
    return shop


@app.get("/api/shops/{slug}", response_model=ShopOut)
def get_shop(slug: str, db: Session = Depends(get_db)):
    return find_shop(slug, db)


@app.post("/api/shops/{slug}/products", response_model=list[ProductOut], status_code=201)
def add_products(slug: str, payload: ProductListIn | list[ProductIn], db: Session = Depends(get_db)):
    shop = find_shop(slug, db)
    items = payload.products if isinstance(payload, ProductListIn) else payload
    products = [Product(shop_id=shop.id, **item.model_dump()) for item in items]
    db.add_all(products); db.commit()
    return products


@app.put("/api/shops/{slug}/products/{product_id}", response_model=ProductOut)
def update_product(slug: str, product_id: int, payload: ProductIn, db: Session = Depends(get_db)):
    shop = find_shop(slug, db)
    product = db.scalar(select(Product).where(Product.id == product_id, Product.shop_id == shop.id))
    if product is None: raise HTTPException(404, "Product not found")
    for key, value in payload.model_dump().items(): setattr(product, key, value)
    db.commit(); db.refresh(product); return product


@app.delete("/api/shops/{slug}/products/{product_id}", status_code=204)
def delete_product(slug: str, product_id: int, db: Session = Depends(get_db)):
    shop = find_shop(slug, db)
    product = db.scalar(select(Product).where(Product.id == product_id, Product.shop_id == shop.id))
    if product is None: raise HTTPException(404, "Product not found")
    db.delete(product); db.commit()


@app.post("/api/shops/{slug}/extract", response_model=list[ProductDraft])
async def extract(slug: str, images: Annotated[list[UploadFile], File()] = [], text: Annotated[str | None, Form()] = None, db: Session = Depends(get_db)):
    find_shop(slug, db)
    if not 1 <= len(images) <= 5:
        raise HTTPException(400, "Upload between 1 and 5 images")
    if text and len(text) > 2000:
        raise HTTPException(400, "Text must be at most 2000 characters")
    image_bytes = []
    allowed = {"image/jpeg", "image/png", "image/webp"}
    for image in images:
        if image.content_type not in allowed:
            raise HTTPException(415, "Only JPG, PNG, and WEBP images are allowed")
        data = await image.read()
        if len(data) > 5 * 1024 * 1024:
            raise HTTPException(413, "Each image must be at most 5 MB")
        image_bytes.append(data)
    try:
        result = ai.extract_products(image_bytes, text)
    except NotImplementedError as exc:
        raise HTTPException(501, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, "Product extraction failed") from exc
    try:
        products = [ProductDraft.model_validate(item) for item in result]
    except Exception as exc:
        raise HTTPException(502, "Extractor returned invalid products") from exc
    return products
