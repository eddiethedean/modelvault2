"""Immutable execution plan dataclasses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from modelvault.contracts import PersistenceContract


@dataclass(frozen=True)
class InsertPlan:
    contract: PersistenceContract
    row: dict[str, Any]
    schema_hash: str


@dataclass(frozen=True)
class ReadPlan:
    contract: PersistenceContract
    key: Any


@dataclass(frozen=True)
class UpsertPlan:
    contract: PersistenceContract
    row: dict[str, Any]
    schema_hash: str


@dataclass(frozen=True)
class DeletePlan:
    contract: PersistenceContract
    key: Any


@dataclass(frozen=True)
class CountPlan:
    contract: PersistenceContract


@dataclass(frozen=True)
class FindPlan:
    contract: PersistenceContract
    filters: dict[str, Any]


@dataclass(frozen=True)
class AllPlan:
    contract: PersistenceContract
    limit: int | None = None


@dataclass(frozen=True)
class ValidateAllPlan:
    contract: PersistenceContract
