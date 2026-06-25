"""Storage strategy protocol."""

from __future__ import annotations

from typing import Any, Protocol

from modelvault.backends.base import Backend
from modelvault.contracts import PersistenceContract
from modelvault.plans import (
    AllPlan,
    CountPlan,
    DeletePlan,
    FindPlan,
    InsertPlan,
    ReadPlan,
    UpsertPlan,
)


class StorageStrategy(Protocol):
    def ensure_schema(self, contract: PersistenceContract, backend: Backend) -> None: ...

    def insert(self, plan: InsertPlan, backend: Backend) -> None: ...

    def upsert(self, plan: UpsertPlan, backend: Backend) -> None: ...

    def get(self, plan: ReadPlan, backend: Backend) -> dict[str, Any]: ...

    def delete(self, plan: DeletePlan, backend: Backend) -> None: ...

    def count(self, plan: CountPlan, backend: Backend) -> int: ...

    def find(self, plan: FindPlan, backend: Backend) -> list[dict[str, Any]]: ...

    def all(self, plan: AllPlan, backend: Backend) -> list[dict[str, Any]]: ...
