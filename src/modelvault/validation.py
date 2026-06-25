"""Validation service for read and write boundaries."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from modelvault.errors import ValidationError
from modelvault.reports import ValidationErrorEntry, ValidationReport


def validate_write(
    model_or_dict: BaseModel | dict[str, Any],
    model_type: type[BaseModel],
) -> BaseModel:
    """Validate and coerce input before persistence."""
    try:
        if isinstance(model_or_dict, BaseModel):
            if not isinstance(model_or_dict, model_type):
                return model_type.model_validate(model_or_dict.model_dump())
            return model_type.model_validate(model_or_dict.model_dump())
        return model_type.model_validate(model_or_dict)
    except PydanticValidationError as exc:
        raise ValidationError("Write validation failed", details=exc.errors()) from exc


def validate_read(payload: dict[str, Any], model_type: type[BaseModel]) -> BaseModel:
    """Validate a deserialized payload after read."""
    try:
        return model_type.model_validate(payload)
    except PydanticValidationError as exc:
        raise ValidationError("Read validation failed", details=exc.errors()) from exc


def validate_many(
    payloads: list[tuple[Any, dict[str, Any]]],
    model_type: type[BaseModel],
) -> ValidationReport:
    """Validate many payloads, collecting errors instead of raising."""
    report = ValidationReport()
    for record_key, payload in payloads:
        try:
            validate_read(payload, model_type)
            report.valid_count += 1
        except ValidationError as exc:
            report.invalid_count += 1
            errors = exc.details if isinstance(exc.details, list) else []
            report.errors.append(ValidationErrorEntry(record_key=record_key, errors=errors))
    return report


def validation_error_json(exc: ValidationError) -> str:
    return json.dumps(exc.details, default=str)
