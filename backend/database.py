"""Database setup for the DukaanAI backend."""

import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dukaanai.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_tables() -> None:
    """Create tables and repair the small schema changes used by this app."""
    Base.metadata.create_all(bind=engine)
    # SQLite's create_all does not add columns to an existing table.  Older
    # demo databases predate product images, so repair that schema in place.
    if engine.dialect.name == "sqlite":
        columns = {column["name"] for column in inspect(engine).get_columns("products")}
        if "image_url" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(2048)"))


def seed_demo_boutique(uploads_dir: Path) -> None:
    """Insert the deterministic demo shop and its local image placeholders once."""
    from .models import Product, Shop

    uploads_dir.mkdir(parents=True, exist_ok=True)
    placeholders = {
        "red-kurta.svg": "#c62828", "blue-jeans.svg": "#1565c0",
        "namkeen.svg": "#ef6c00", "cotton-saree.svg": "#8e24aa",
        "leather-sandals.svg": "#6d4c41", "tea.svg": "#2e7d32",
        "steel-bottle.svg": "#546e7a",
    }
    for filename, color in placeholders.items():
        path = uploads_dir / filename
        if not path.exists():
            path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480"><rect width="100%" height="100%" fill="{color}"/><text x="50%" y="50%" text-anchor="middle" fill="white" font-size="32">DukaanAI</text></svg>', encoding="utf-8")
    with SessionLocal() as db:
        shop = db.query(Shop).filter_by(slug="demo-boutique").first()
        if shop is not None:
            return
        shop = Shop(name="Demo Boutique", whatsapp_number="+919876543210", slug="demo-boutique")
        db.add(shop)
        db.flush()
        items = [("Red Cotton Kurta", 499, 18, "Fashion", "red-kurta.svg", ["S", "M", "L", "XL"]), ("Classic Blue Jeans", 899, 12, "Fashion", "blue-jeans.svg", ["30", "32", "34"]), ("Masala Namkeen (Pack)", 120, 24, "Groceries", "namkeen.svg", ["1 pack", "2 packs"]), ("Handloom Cotton Saree", 1299, 7, "Fashion", "cotton-saree.svg", ["Free Size"]), ("Leather Kolhapuri Sandals", 699, 10, "Footwear", "leather-sandals.svg", ["7", "8", "9", "10"]), ("Premium Assam Tea", 249, 20, "Groceries", "tea.svg", ["250g", "500g"]), ("Insulated Steel Bottle", 599, 14, "Home", "steel-bottle.svg", ["750ml"])]
        db.add_all([Product(shop_id=shop.id, name=name, price=price, stock=stock, category=category, variants=variants, image_url=f"/uploads/{image}") for name, price, stock, category, image, variants in items])
        db.commit()


def get_db():
    """Yield a database session for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
