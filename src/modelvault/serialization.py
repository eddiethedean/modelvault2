"""Model serialization and deserialization for storage."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from modelvault.contracts import FieldDefinition, PersistenceContract


def _field_map(contract: PersistenceContract) -> dict[str, FieldDefinition]:
    return {field.name: field for field in contract.fields}


def _encode_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, BaseModel):
        return json.dumps(value.model_dump(mode="json"), sort_keys=True)
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, default=str)
    return value


def _decode_value(
    name: str,
    value: Any,
    field_def: FieldDefinition,
    model_type: type[BaseModel],
) -> Any:
    if value is None:
        return None
    if not field_def.is_json_column:
        annotation = model_type.model_fields[name].annotation
        return _decode_scalar(value, annotation)
    if isinstance(value, str):
        return json.loads(value)
    return value


def _decode_scalar(value: Any, annotation: Any) -> Any:
    import typing

    origin = getattr(annotation, "__origin__", None)
    if origin is typing.Union:
        args = [a for a in annotation.__args__ if a is not type(None)]
        if args:
            annotation = args[0]

    if annotation is datetime and isinstance(value, str):
        return datetime.fromisoformat(value)
    if annotation is date and isinstance(value, str):
        return date.fromisoformat(value)
    if annotation is UUID and isinstance(value, str):
        return UUID(value)
    if annotation is Decimal and isinstance(value, str):
        return Decimal(value)
    if isinstance(annotation, type) and issubclass(annotation, Enum) and isinstance(value, str):
        return annotation(value)
    return value


def serialize_model(model: BaseModel, contract: PersistenceContract) -> dict[str, Any]:
    """Serialize a validated model into database-safe row values."""
    raw = model.model_dump(mode="python")
    fields = _field_map(contract)
    row: dict[str, Any] = {}
    for name, value in raw.items():
        field_def = fields[name]
        if field_def.is_json_column:
            row[name] = _encode_value(value)
        else:
            row[name] = _encode_value(value)
    return row


def deserialize_payload(payload: dict[str, Any], model_type: type[BaseModel]) -> dict[str, Any]:
    """Convert database row values into a model payload dict."""
    field_defs = {
        name: FieldDefinition(
            name=name,
            type_name=str(field_info.annotation),
            required=field_info.is_required(),
            has_default=not field_info.is_required(),
            is_json_column=_is_json_annotation(field_info.annotation),
        )
        for name, field_info in model_type.model_fields.items()
    }
    decoded: dict[str, Any] = {}
    for name, value in payload.items():
        if name.startswith("__modelvault_"):
            continue
        if name not in field_defs:
            continue
        decoded[name] = _decode_value(name, value, field_defs[name], model_type)
    return decoded


def _is_json_annotation(annotation: Any) -> bool:
    import typing

    origin = getattr(annotation, "__origin__", None)
    if origin is typing.Union:
        args = [a for a in annotation.__args__ if a is not type(None)]
        if args:
            annotation = args[0]
            origin = getattr(annotation, "__origin__", None)
    if annotation in (list, dict):
        return True
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return True
    if origin in (list, dict):
        return True
    return False
