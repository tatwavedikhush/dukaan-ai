import json

import pytest

from backend.ai import GeminiExtractor, ExtractionError, MockExtractor, _products, parse_price


def test_mock_extractor_returns_one_product_per_sample_image() -> None:
    images = [b"kurta", b"jeans", b"namkeen"]
    text = "red kurta 499\nblue jeans Rs 899 sizes 30 32\n2 packs namkeen 120 each"
    products = MockExtractor().extract(images, text, ["red-kurta.png", "blue-jeans.png", "namkeen-pack.png"])
    assert len(products) == 3
    assert [product["name"] for product in products] == ["Red Cotton Kurta", "Classic Blue Jeans", "Masala Namkeen"]


def test_partial_product_json_is_rejected() -> None:
    with pytest.raises(Exception):
        _products([{"name": "Missing price"}])


def test_gemini_retries_malformed_json(monkeypatch: pytest.MonkeyPatch) -> None:
    extractor = object.__new__(GeminiExtractor)
    calls = iter(["not json", json.dumps([{"name": "Tea", "price": "Rs 20"}])])
    monkeypatch.setattr(extractor, "_request", lambda images, text: next(calls))
    assert extractor.extract([], None)[0]["price"] == 20


def test_gemini_failure_is_safe(monkeypatch: pytest.MonkeyPatch) -> None:
    extractor = object.__new__(GeminiExtractor)
    monkeypatch.setattr(extractor, "_request", lambda images, text: "{}")
    with pytest.raises(ExtractionError, match="Product extraction failed"):
        extractor.extract([], None)
