"""Execution planner — produces immutable plans without database access."""

from __future__ import annotations

from typing import Any

from modelvault.contracts import PersistenceContract
from modelvault.errors import PlanningError
from modelvault.fingerprint import fingerprint_contract
from modelvault.plans import (
    AllPlan,
    CountPlan,
    DeletePlan,
    FindPlan,
    InsertPlan,
    ReadPlan,
    UpsertPlan,
    ValidateAllPlan,
)


class Planner:
    """Transform contracts and operations into execution plans."""

    def plan_insert(
        self,
        contract: PersistenceContract,
        row: dict[str, Any],
    ) -> InsertPlan:
        return InsertPlan(
            contract=contract,
            row=dict(row),
            schema_hash=fingerprint_contract(contract),
        )

    def plan_read(self, contract: PersistenceContract, key: Any) -> ReadPlan:
        return ReadPlan(contract=contract, key=key)

    def plan_upsert(
        self,
        contract: PersistenceContract,
        row: dict[str, Any],
    ) -> UpsertPlan:
        return UpsertPlan(
            contract=contract,
            row=dict(row),
            schema_hash=fingerprint_contract(contract),
        )

    def plan_delete(self, contract: PersistenceContract, key: Any) -> DeletePlan:
        return DeletePlan(contract=contract, key=key)

    def plan_count(self, contract: PersistenceContract) -> CountPlan:
        return CountPlan(contract=contract)

    def plan_find(self, contract: PersistenceContract, filters: dict[str, Any]) -> FindPlan:
        self._validate_filters(contract, filters)
        return FindPlan(contract=contract, filters=dict(filters))

    def plan_all(self, contract: PersistenceContract, limit: int | None = None) -> AllPlan:
        return AllPlan(contract=contract, limit=limit)

    def plan_validate_all(self, contract: PersistenceContract) -> ValidateAllPlan:
        return ValidateAllPlan(contract=contract)

    def _validate_filters(self, contract: PersistenceContract, filters: dict[str, Any]) -> None:
        field_names = {field.name for field in contract.fields}
        for key in filters:
            if key not in field_names:
                raise PlanningError(f"Unknown filter field {key!r}")
