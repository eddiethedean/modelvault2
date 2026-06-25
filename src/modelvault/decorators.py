"""Persistence contract decorator for Pydantic models."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, TypeVar

ModelT = TypeVar("ModelT", bound=type)


def model(
    *,
    key: str,
    storage: str = "table",
    indexes: Sequence[str] | None = None,
    table_name: str | None = None,
) -> Callable[[ModelT], ModelT]:
    """Attach ModelVault persistence metadata to a Pydantic model class."""

    def decorator(cls: ModelT) -> ModelT:
        config: dict[str, Any] = {
            "key": key,
            "storage": storage,
            "indexes": tuple(indexes or ()),
            "table_name": table_name,
        }
        cls.__modelvault_config__ = config  # type: ignore[attr-defined]
        return cls

    return decorator
