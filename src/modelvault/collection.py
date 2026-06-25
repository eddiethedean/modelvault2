"""Typed repository for a single Pydantic model."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from modelvault.backends.base import Backend
from modelvault.contracts import PersistenceContract
from modelvault.errors import RecordNotFoundError, ValidationError
from modelvault.planner import Planner
from modelvault.plans import AllPlan
from modelvault.registry import Registry
from modelvault.reports import ValidationReport
from modelvault.serialization import deserialize_payload, serialize_model
from modelvault.storage.table import TableStorage
from modelvault.validation import (
    validate_many,
    validate_read,
    validate_write,
    validation_error_json,
)

T = TypeVar("T", bound=BaseModel)


class Collection(Generic[T]):
    """Typed CRUD interface for one model type."""

    def __init__(
        self,
        contract: PersistenceContract,
        backend: Backend,
        registry: Registry,
        planner: Planner | None = None,
        storage: TableStorage | None = None,
    ) -> None:
        self._contract = contract
        self._backend = backend
        self._registry = registry
        self._planner = planner or Planner()
        self._storage = storage or TableStorage()
        self._model_type: type[T] = contract.model_type  # type: ignore[assignment]

    @property
    def contract(self) -> PersistenceContract:
        return self._contract

    def insert(self, model: T | dict[str, Any]) -> T:
        validated = validate_write(model, self._model_type)
        row = serialize_model(validated, self._contract)
        plan = self._planner.plan_insert(self._contract, row)
        self._storage.insert(plan, self._backend)
        return validated

    def upsert(self, model: T | dict[str, Any]) -> T:
        validated = validate_write(model, self._model_type)
        row = serialize_model(validated, self._contract)
        plan = self._planner.plan_upsert(self._contract, row)
        self._storage.upsert(plan, self._backend)
        return validated

    def get(self, key: Any) -> T:
        plan = self._planner.plan_read(self._contract, key)
        try:
            payload = self._storage.get(plan, self._backend)
        except RecordNotFoundError:
            raise
        decoded = deserialize_payload(payload, self._model_type)
        return validate_read(decoded, self._model_type)  # type: ignore[return-value]

    def delete(self, key: Any) -> None:
        plan = self._planner.plan_delete(self._contract, key)
        self._storage.delete(plan, self._backend)

    def exists(self, key: Any) -> bool:
        try:
            self.get(key)
            return True
        except RecordNotFoundError:
            return False

    def count(self) -> int:
        plan = self._planner.plan_count(self._contract)
        return self._storage.count(plan, self._backend)

    def all(self, limit: int | None = None) -> list[T]:
        plan = self._planner.plan_all(self._contract, limit=limit)
        rows = self._storage.all(plan, self._backend)
        return [self._load_row(row) for row in rows]

    def find(self, **filters: Any) -> list[T]:
        plan = self._planner.plan_find(self._contract, filters)
        rows = self._storage.find(plan, self._backend)
        return [self._load_row(row) for row in rows]

    def validate_all(self) -> ValidationReport:
        plan = self._planner.plan_validate_all(self._contract)
        all_plan = AllPlan(contract=plan.contract)
        rows = self._storage.all(all_plan, self._backend)
        key_field = self._contract.key.field
        payloads: list[tuple[Any, dict[str, Any]]] = []
        for row in rows:
            key = row.get(key_field)
            decoded = deserialize_payload(row, self._model_type)
            payloads.append((key, decoded))
        report = validate_many(payloads, self._model_type)
        for entry in report.errors:
            self._registry.record_validation_event(
                self._contract.collection_name,
                str(entry.record_key) if entry.record_key is not None else None,
                "read",
                "invalid",
                validation_error_json(ValidationError("bulk", details=entry.errors)),
            )
        return report

    def _load_row(self, row: dict[str, Any]) -> T:
        decoded = deserialize_payload(row, self._model_type)
        return validate_read(decoded, self._model_type)  # type: ignore[return-value]
