"""Shared typing aliases for ModelVault."""

from typing import Any, TypeVar

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

JsonDict = dict[str, Any]
