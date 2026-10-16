"""Interfaces and local implementations for document extraction."""

from collections.abc import Mapping
from typing import Protocol


class Extractor(Protocol):
    """Extract structured fields from an input document."""

    def extract(self, document: str) -> Mapping[str, str]:
        ...


class MockExtractor:
    """Deterministic extractor used in development and tests."""

    def extract(self, document: str) -> Mapping[str, str]:
        if not document or not document.strip():
            return {}
        fields: dict[str, str] = {}
        for line in document.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                if key.strip() and value.strip():
                    fields[key.strip().lower()] = value.strip()
        return fields
