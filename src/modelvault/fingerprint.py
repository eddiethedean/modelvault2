"""Deterministic persistence contract fingerprinting."""

from __future__ import annotations

import hashlib
import json

from modelvault.contracts import PersistenceContract

FINGERPRINT_VERSION = "1"


def _contract_payload(contract: PersistenceContract) -> dict:
    return {
        "fingerprint_version": FINGERPRINT_VERSION,
        "model_name": contract.model_name,
        "python_path": contract.python_path,
        "key_field": contract.key.field,
        "storage_mode": contract.storage.mode,
        "table_name": contract.table_name,
        "indexes": sorted(idx.fields[0] for idx in contract.indexes),
        "fields": [
            {
                "name": field.name,
                "type": field.type_name,
                "required": field.required,
                "has_default": field.has_default,
                "is_json_column": field.is_json_column,
            }
            for field in contract.fields
        ],
    }


def fingerprint_contract(contract: PersistenceContract) -> str:
    """Return a deterministic SHA-256 hex digest for a persistence contract."""
    payload = _contract_payload(contract)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
