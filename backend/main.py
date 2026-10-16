"""FastAPI application entry point."""

from fastapi import FastAPI

from .database import create_tables

app = FastAPI(title="DukaanAI API")


@app.on_event("startup")
def initialize_database() -> None:
    create_tables()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
