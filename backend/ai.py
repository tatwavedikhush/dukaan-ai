"""Product extraction implementations used by the extraction endpoint."""

from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request
from collections.abc import Sequence
from typing import Any, Protocol

from pydantic import BaseModel, Field, ValidationError


class Extractor(Protocol):
    def extract(self, images: Sequence[bytes], text: str | None = None) -> Sequence[dict]: ...


class ExtractionError(RuntimeError):
    """A safe, user-facing extraction failure (without provider details)."""


class ExtractedProduct(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    currency: str = "INR"
    description: str = ""
    category: str = "General"
    variants: list[str] = []


def parse_price(value: Any) -> float:
    """Parse common Indian price spellings into a non-negative number."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value >= 0:
            return float(value)
    raw = str(value).strip().lower().replace(",", "")
    words = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
             "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
             "ninety": 90, "hundred": 100}
    match = re.search(r"(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)", raw)
    if match:
        return float(match.group(1))
    tokens = re.findall(r"[a-z]+", raw)
    if tokens and all(token in words for token in tokens):
        if len(tokens) == 3 and tokens[1] == "ninety" and tokens[0] in words and tokens[2] in words:
            # Common spoken-price shorthand: “four ninety nine” means 499.
            return float(words[tokens[0]] * 100 + words[tokens[1]] + words[tokens[2]])
        if "hundred" in tokens:
            before = tokens[:tokens.index("hundred")]
            return float(sum(words[t] for t in before) * 100 + sum(words[t] for t in tokens[tokens.index("hundred") + 1:]))
        if "ninety" in tokens and any(t in words for t in tokens if t != "ninety"):
            return float(90 + sum(words[t] for t in tokens if t != "ninety"))
        return float(sum(words[t] for t in tokens))
    raise ValueError("invalid price")


def _products(items: Any) -> list[dict]:
    if not isinstance(items, list):
        raise ValueError("products must be a list")
    result = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("invalid product")
        data = dict(item)
        data["price"] = parse_price(data.get("price"))
        result.append(ExtractedProduct.model_validate(data).model_dump())
    return result


class MockExtractor:
    """Stable local data for demos and offline development."""

    def extract(self, images: Sequence[bytes], text: str | None = None) -> list[dict]:
        source = (text or "").lower()
        if "biscuit" in source or "cookie" in source:
            items = [{"name": "Parle-G Biscuits", "price": "₹10/-", "stock": 24, "category": "Groceries"},
                     {"name": "Good Day Cookies", "price": "four ninety nine", "stock": 12, "category": "Groceries"}]
        elif "soap" in source:
            items = [{"name": "Neem Soap", "price": "Rs 49", "stock": 18, "category": "Personal Care"},
                     {"name": "Bath Soap", "price": "₹75/-", "stock": 10, "category": "Personal Care"}]
        else:
            items = [{"name": "Masala Tea", "price": "Rs 499", "stock": 15, "category": "Groceries"},
                     {"name": "Basmati Rice", "price": "₹120/-", "stock": 8, "category": "Groceries"}]
        return _products(items)


class GeminiExtractor:
    """Gemini REST extractor with one bounded retry and strict validation."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ExtractionError("Gemini extraction is not configured")

    def _request(self, images: Sequence[bytes], text: str | None) -> str:
        parts: list[dict[str, Any]] = [{"text": "Return ONLY a JSON array of products with name, price, and stock. Price may be numeric or a rupee string. No markdown."}]
        if text:
            parts.append({"text": text})
        for image in images:
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image).decode("ascii")}})
        payload = {"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json"}}
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + self.api_key
        request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read())
        return body["candidates"][0]["content"]["parts"][0]["text"]

    def extract(self, images: Sequence[bytes], text: str | None = None) -> list[dict]:
        for _ in range(2):
            try:
                return _products(json.loads(self._request(images, text)))
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError, ValidationError):
                continue
        raise ExtractionError("Product extraction failed")


def extract_products(images: Sequence[bytes], text: str | None = None) -> Sequence[dict]:
    extractor: Extractor = MockExtractor() if os.getenv("MOCK_AI", "false").lower() == "true" else GeminiExtractor()
    return extractor.extract(images, text)
