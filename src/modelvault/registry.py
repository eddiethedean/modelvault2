"""Contract registry service."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import insert, select, update

from modelvault._version import __version__
from modelvault.backends.base import Backend
from modelvault.contracts import PersistenceContract
from modelvault.errors import DriftError
from modelvault.fingerprint import FINGERPRINT_VERSION, fingerprint_contract
from modelvault.metadata.tables import (
    metadata,
    registry_table,
    schemas_table,
    validation_events_table,
)
from modelvault.reports import DriftReport, StoredContract


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Registry:
    """Persistent catalog of ModelVault contracts."""

    def __init__(self, backend: Backend) -> None:
        self._backend = backend

    def ensure_metadata(self) -> None:
        with self._backend.begin() as conn:
            metadata.create_all(conn)

    def register_contract(self, contract: PersistenceContract) -> None:
        self.ensure_metadata()
        contract_hash = fingerprint_contract(contract)
        existing = self.get_contract(contract.collection_name)
        now = _utc_now()

        if existing is None:
            with self._backend.begin() as conn:
                conn.execute(
                    insert(registry_table).values(
                        collection_name=contract.collection_name,
                        model_name=contract.model_name,
                        python_path=contract.python_path,
                        table_name=contract.table_name,
                        storage_mode=contract.storage.mode,
                        key_field=contract.key.field,
                        contract_hash=contract_hash,
                        created_at=now,
                        updated_at=now,
                    )
                )
                conn.execute(
                    insert(schemas_table).values(
                        collection_name=contract.collection_name,
                        contract_hash=contract_hash,
                        schema_json=contract.schema_json,
                        modelvault_version=__version__,
                        fingerprint_version=FINGERPRINT_VERSION,
                        created_at=now,
                    )
                )
            return

        if existing.contract_hash == contract_hash:
            return

        raise DriftError(
            f"Contract drift detected for collection {contract.collection_name!r}",
            details=DriftReport(
                collection_name=contract.collection_name,
                stored_hash=existing.contract_hash,
                current_hash=contract_hash,
            ),
        )

    def get_contract(self, collection_name: str) -> StoredContract | None:
        row = self._backend.fetch_one(
            select(registry_table).where(registry_table.c.collection_name == collection_name)
        )
        if row is None:
            return None
        mapping = row._mapping
        schema_row = self._backend.fetch_one(
            select(schemas_table)
            .where(schemas_table.c.collection_name == collection_name)
            .where(schemas_table.c.contract_hash == mapping["contract_hash"])
            .order_by(schemas_table.c.id.desc())
            .limit(1)
        )
        schema_json = schema_row._mapping["schema_json"] if schema_row else "{}"
        return StoredContract(
            collection_name=mapping["collection_name"],
            model_name=mapping["model_name"],
            python_path=mapping["python_path"],
            table_name=mapping["table_name"],
            storage_mode=mapping["storage_mode"],
            key_field=mapping["key_field"],
            contract_hash=mapping["contract_hash"],
            schema_json=schema_json,
            created_at=mapping["created_at"],
            updated_at=mapping["updated_at"],
        )

    def list_contracts(self) -> list[StoredContract]:
        rows = self._backend.fetch_all(select(registry_table))
        contracts: list[StoredContract] = []
        for row in rows:
            stored = self.get_contract(row._mapping["collection_name"])
            if stored is not None:
                contracts.append(stored)
        return contracts

    def record_validation_event(
        self,
        collection_name: str,
        record_key: str | None,
        direction: str,
        status: str,
        error_json: str | None,
    ) -> None:
        self.ensure_metadata()
        with self._backend.begin() as conn:
            conn.execute(
                insert(validation_events_table).values(
                    collection_name=collection_name,
                    record_key=record_key,
                    direction=direction,
                    status=status,
                    error_json=error_json,
                    created_at=_utc_now(),
                )
            )

    def detect_drift(self, contract: PersistenceContract) -> DriftReport | None:
        existing = self.get_contract(contract.collection_name)
        if existing is None:
            return None
        current_hash = fingerprint_contract(contract)
        if existing.contract_hash == current_hash:
            return None
        return DriftReport(
            collection_name=contract.collection_name,
            stored_hash=existing.contract_hash,
            current_hash=current_hash,
        )

    def touch_contract(self, contract: PersistenceContract) -> None:
        """Update registry updated_at without changing hash (internal use)."""
        with self._backend.begin() as conn:
            conn.execute(
                update(registry_table)
                .where(registry_table.c.collection_name == contract.collection_name)
                .values(updated_at=_utc_now())
            )
