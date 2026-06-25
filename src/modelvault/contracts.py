"""Persistence contract data structures and builder."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel

from modelvault.errors import ContractError

STORAGE_TABLE = "table"


@dataclass(frozen=True)
class KeyDefinition:
    field: str
    type_name: str
    required: bool = True


@dataclass(frozen=True)
class StorageDefinition:
    mode: Literal["table", "document", "hybrid"]
    table_name: str
    column_fields: tuple[str, ...]
    json_fields: tuple[str, ...]


@dataclass(frozen=True)
class IndexDefinition:
    fields: tuple[str, ...]
    unique: bool = False
    name: str | None = None


@dataclass(frozen=True)
class ValidationDefinition:
    on_write: Literal["strict", "warn", "disabled"] = "strict"
    on_read: Literal["strict", "warn", "disabled"] = "strict"
    on_bulk: Literal["strict", "report"] = "strict"


@dataclass(frozen=True)
class FieldDefinition:
    name: str
    type_name: str
    required: bool
    has_default: bool
    is_json_column: bool


@dataclass(frozen=True)
class PersistenceContract:
    model_type: type[BaseModel]
    model_name: str
    python_path: str
    collection_name: str
    table_name: str
    key: KeyDefinition
    storage: StorageDefinition
    indexes: tuple[IndexDefinition, ...]
    fields: tuple[FieldDefinition, ...]
    schema_json: str
    validation: ValidationDefinition


def _default_table_name(model_name: str) -> str:
    return f"{model_name.lower()}s"


def _python_path(model_type: type[BaseModel]) -> str:
    return f"{model_type.__module__}.{model_type.__qualname__}"


def _unwrap_optional(annotation: Any) -> tuple[Any, bool]:
    origin = getattr(annotation, "__origin__", None)
    if origin is not None:
        import typing

        if origin is typing.Union:
            args = [a for a in annotation.__args__ if a is not type(None)]
            if len(args) == 1:
                return args[0], True
    return annotation, False


def _type_name(annotation: Any) -> str:
    annotation, _ = _unwrap_optional(annotation)
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation).replace("typing.", "")


def _is_json_column(annotation: Any, field_info: Any) -> bool:
    annotation, _ = _unwrap_optional(annotation)
    if annotation in (list, dict):
        return True
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return True
    origin = getattr(annotation, "__origin__", None)
    if origin in (list, dict):
        return True
    return False


def _field_definitions(model_type: type[BaseModel]) -> tuple[FieldDefinition, ...]:
    fields: list[FieldDefinition] = []
    for name, field_info in model_type.model_fields.items():
        annotation = field_info.annotation
        required = field_info.is_required()
        has_default = not required
        fields.append(
            FieldDefinition(
                name=name,
                type_name=_type_name(annotation),
                required=required,
                has_default=has_default,
                is_json_column=_is_json_column(annotation, field_info),
            )
        )
    return tuple(fields)


def _get_config(model_type: type[BaseModel], overrides: dict[str, Any] | None) -> dict[str, Any]:
    base: dict[str, Any] = {}
    if hasattr(model_type, "__modelvault_config__"):
        base = dict(model_type.__modelvault_config__)  # type: ignore[attr-defined]
    if overrides:
        base.update(overrides)
    return base


def build_contract(
    model_type: type[BaseModel],
    overrides: dict[str, Any] | None = None,
) -> PersistenceContract:
    """Build a persistence contract from a Pydantic model and optional overrides."""
    if not isinstance(model_type, type) or not issubclass(model_type, BaseModel):
        raise ContractError(f"{model_type!r} is not a Pydantic BaseModel subclass")

    config = _get_config(model_type, overrides)
    key_field = config.get("key")
    if not key_field:
        raise ContractError("Persistence contract requires a key field")

    storage_mode = config.get("storage", STORAGE_TABLE)
    if storage_mode != STORAGE_TABLE:
        raise ContractError(
            f"Unsupported storage mode {storage_mode!r}; v0.17 supports 'table' only"
        )

    field_defs = _field_definitions(model_type)
    field_names = {f.name for f in field_defs}
    if key_field not in field_names:
        raise ContractError(
            f"Key field {key_field!r} does not exist on model {model_type.__name__}"
        )

    index_fields: tuple[str, ...] = tuple(config.get("indexes") or ())
    for index_field in index_fields:
        if index_field not in field_names:
            raise ContractError(
                f"Index field {index_field!r} does not exist on model {model_type.__name__}"
            )

    table_name = config.get("table_name") or _default_table_name(model_type.__name__)
    collection_name = table_name

    key_def = next(f for f in field_defs if f.name == key_field)
    key = KeyDefinition(field=key_field, type_name=key_def.type_name, required=key_def.required)

    column_fields = tuple(f.name for f in field_defs if not f.is_json_column)
    json_fields = tuple(f.name for f in field_defs if f.is_json_column)
    storage = StorageDefinition(
        mode="table",
        table_name=table_name,
        column_fields=column_fields,
        json_fields=json_fields,
    )

    indexes = tuple(
        IndexDefinition(fields=(field,), unique=False, name=f"ix_{table_name}_{field}")
        for field in index_fields
    )

    schema_json = json.dumps(model_type.model_json_schema(), sort_keys=True)

    return PersistenceContract(
        model_type=model_type,
        model_name=model_type.__name__,
        python_path=_python_path(model_type),
        collection_name=collection_name,
        table_name=table_name,
        key=key,
        storage=storage,
        indexes=indexes,
        fields=field_defs,
        schema_json=schema_json,
        validation=ValidationDefinition(),
    )


__all__ = [
    "PersistenceContract",
    "KeyDefinition",
    "StorageDefinition",
    "IndexDefinition",
    "ValidationDefinition",
    "FieldDefinition",
    "build_contract",
    "STORAGE_TABLE",
]
