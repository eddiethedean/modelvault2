"""Structured report types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationErrorEntry:
    record_key: Any | None
    errors: list[dict[str, Any]]


@dataclass
class ValidationReport:
    valid_count: int = 0
    invalid_count: int = 0
    errors: list[ValidationErrorEntry] = field(default_factory=list)


@dataclass(frozen=True)
class DriftReport:
    collection_name: str
    stored_hash: str
    current_hash: str
    status: str = "drift_detected"


@dataclass(frozen=True)
class CollectionHealth:
    collection_name: str
    table_name: str
    contract_hash: str
    stored_hash: str | None
    drift_detected: bool
    table_exists: bool
    record_count: int | None = None


@dataclass
class HealthReport:
    backend_ok: bool = False
    metadata_ok: bool = False
    healthy: bool = False
    collections: list[CollectionHealth] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CollectionDescription:
    collection_name: str
    model_name: str
    table_name: str
    storage_mode: str
    key_field: str
    contract_hash: str
    stored_hash: str | None
    drift_detected: bool
    record_count: int


@dataclass(frozen=True)
class StoredContract:
    collection_name: str
    model_name: str
    python_path: str
    table_name: str
    storage_mode: str
    key_field: str
    contract_hash: str
    schema_json: str
    created_at: str
    updated_at: str
