"""Vault root coordinator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from modelvault.backends.sqlite import SQLiteBackend
from modelvault.collection import Collection
from modelvault.contracts import PersistenceContract, build_contract
from modelvault.errors import BackendError, DriftError
from modelvault.fingerprint import fingerprint_contract
from modelvault.planner import Planner
from modelvault.registry import Registry
from modelvault.reports import CollectionDescription, CollectionHealth, HealthReport
from modelvault.storage.table import TableStorage


class Vault:
    """Root coordinator for ModelVault persistence."""

    def __init__(self, url: str, *, echo: bool = False) -> None:
        if not url.startswith("sqlite:///"):
            raise BackendError(f"v0.17 supports SQLite URLs only, got {url!r}")
        self._url = url
        path = url.removeprefix("sqlite:///")
        self._backend = SQLiteBackend.from_path(path, echo=echo)
        self._registry = Registry(self._backend)
        self._planner = Planner()
        self._storage = TableStorage()
        self._registered: dict[type[BaseModel], PersistenceContract] = {}
        self._collections: dict[type[BaseModel], Collection[Any]] = {}

    @classmethod
    def sqlite(cls, path: str | Path) -> Vault:
        resolved = Path(path).resolve()
        return cls(f"sqlite:///{resolved}")

    def register(self, model_type: type[BaseModel], **options: Any) -> None:
        contract = build_contract(model_type, options or None)
        self._registry.register_contract(contract)
        self._storage.ensure_schema(contract, self._backend)
        self._registered[model_type] = contract

    def collection(self, model_type: type[BaseModel]) -> Collection[Any]:
        if model_type in self._collections:
            return self._collections[model_type]

        contract = self._registered.get(model_type)
        if contract is None:
            contract = build_contract(model_type)
            self._registry.register_contract(contract)
            self._storage.ensure_schema(contract, self._backend)
            self._registered[model_type] = contract

        collection = Collection(
            contract=contract,
            backend=self._backend,
            registry=self._registry,
            planner=self._planner,
            storage=self._storage,
        )
        self._collections[model_type] = collection
        return collection

    def models(self) -> list[type[BaseModel]]:
        return list(self._registered.keys())

    def describe(self, model_type: type[BaseModel]) -> CollectionDescription:
        contract = self._registered.get(model_type) or build_contract(model_type)
        stored = self._registry.get_contract(contract.collection_name)
        current_hash = fingerprint_contract(contract)
        drift = stored is not None and stored.contract_hash != current_hash
        count = 0
        if model_type in self._collections or stored is not None:
            try:
                count = self.collection(model_type).count()
            except DriftError:
                count = 0
        return CollectionDescription(
            collection_name=contract.collection_name,
            model_name=contract.model_name,
            table_name=contract.table_name,
            storage_mode=contract.storage.mode,
            key_field=contract.key.field,
            contract_hash=current_hash,
            stored_hash=stored.contract_hash if stored else None,
            drift_detected=drift,
            record_count=count,
        )

    def health(self) -> HealthReport:
        report = HealthReport()
        try:
            health = self._backend.health()
            report.backend_ok = bool(health.get("ok"))
        except Exception as exc:
            report.messages.append(str(exc))
            report.backend_ok = False

        try:
            self._registry.ensure_metadata()
            report.metadata_ok = self._backend.table_exists("modelvault_registry")
        except Exception as exc:
            report.messages.append(str(exc))
            report.metadata_ok = False

        for model_type, contract in self._registered.items():
            stored = self._registry.get_contract(contract.collection_name)
            current_hash = fingerprint_contract(contract)
            drift = stored is not None and stored.contract_hash != current_hash
            record_count: int | None = None
            try:
                if model_type in self._collections:
                    record_count = self._collections[model_type].count()
                else:
                    record_count = 0
            except Exception:
                record_count = None
            report.collections.append(
                CollectionHealth(
                    collection_name=contract.collection_name,
                    table_name=contract.table_name,
                    contract_hash=current_hash,
                    stored_hash=stored.contract_hash if stored else None,
                    drift_detected=drift,
                    table_exists=self._backend.table_exists(contract.table_name),
                    record_count=record_count,
                )
            )

        report.healthy = report.backend_ok and report.metadata_ok and all(
            not c.drift_detected for c in report.collections
        )
        return report

    def close(self) -> None:
        self._backend.close()
