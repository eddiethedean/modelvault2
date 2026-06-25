"""Table storage strategy for v0.17."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    MetaData,
    Table,
    Text,
    insert,
    text,
)

from modelvault.backends.base import Backend
from modelvault.contracts import FieldDefinition, PersistenceContract
from modelvault.errors import RecordNotFoundError
from modelvault.plans import (
    AllPlan,
    CountPlan,
    DeletePlan,
    FindPlan,
    InsertPlan,
    ReadPlan,
    UpsertPlan,
)

METADATA_COLUMNS = (
    "__modelvault_schema_hash",
    "__modelvault_created_at",
    "__modelvault_updated_at",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sqlalchemy_type(field: FieldDefinition) -> Any:
    if field.is_json_column:
        return Text
    mapping = {
        "str": Text,
        "int": Integer,
        "float": Float,
        "bool": Boolean,
        "datetime": Text,
        "date": Text,
        "UUID": Text,
        "Decimal": Text,
    }
    if field.type_name in mapping:
        return mapping[field.type_name]
    if field.type_name.endswith("Enum"):
        return Text
    return Text


def _build_table(contract: PersistenceContract) -> Table:
    metadata = MetaData()
    columns: list[Column[Any]] = []
    for field in contract.fields:
        col_type = _sqlalchemy_type(field)
        nullable = not field.required
        if field.name == contract.key.field:
            columns.append(Column(field.name, col_type, primary_key=True, nullable=False))
        else:
            columns.append(Column(field.name, col_type, nullable=nullable))
    columns.extend(
        [
            Column("__modelvault_schema_hash", Text, nullable=False),
            Column("__modelvault_created_at", Text, nullable=False),
            Column("__modelvault_updated_at", Text, nullable=False),
        ]
    )
    return Table(contract.table_name, metadata, *columns)


class TableStorage:
    """Map persistence contracts to single SQL tables."""

    def ensure_schema(self, contract: PersistenceContract, backend: Backend) -> None:
        table = _build_table(contract)
        with backend.begin() as conn:
            table.metadata.create_all(conn)
        for index_def in contract.indexes:
            field = index_def.fields[0]
            index_name = index_def.name or f"ix_{contract.table_name}_{field}"
            if not self._index_exists(backend, index_name):
                with backend.begin() as conn:
                    conn.execute(
                        text(
                            f'CREATE INDEX IF NOT EXISTS "{index_name}" '
                            f'ON "{contract.table_name}" ("{field}")'
                        )
                    )

    def _index_exists(self, backend: Backend, index_name: str) -> bool:
        row = backend.fetch_one(
            text("SELECT name FROM sqlite_master WHERE type='index' AND name=:name"),
            {"name": index_name},
        )
        return row is not None

    def _full_row(
        self,
        plan_row: dict[str, Any],
        schema_hash: str,
        *,
        is_insert: bool,
    ) -> dict[str, Any]:
        now = _utc_now()
        row = dict(plan_row)
        row["__modelvault_schema_hash"] = schema_hash
        if is_insert:
            row.setdefault("__modelvault_created_at", now)
        row["__modelvault_updated_at"] = now
        return row

    def insert(self, plan: InsertPlan, backend: Backend) -> None:
        row = self._full_row(plan.row, plan.schema_hash, is_insert=True)
        table = _build_table(plan.contract)
        with backend.begin() as conn:
            conn.execute(insert(table).values(**row))

    def upsert(self, plan: UpsertPlan, backend: Backend) -> None:
        key_field = plan.contract.key.field
        key_value = plan.row[key_field]
        read_plan = ReadPlan(contract=plan.contract, key=key_value)
        try:
            self.get(read_plan, backend)
            row = self._full_row(plan.row, plan.schema_hash, is_insert=False)
            assignments = {k: v for k, v in row.items() if k != key_field}
            set_clause = ", ".join(f'"{k}" = :{k}' for k in assignments)
            params = dict(assignments)
            params[key_field] = key_value
            with backend.begin() as conn:
                sql = (
                    f'UPDATE "{plan.contract.table_name}" SET {set_clause} '
                    f'WHERE "{key_field}" = :{key_field}'
                )
                conn.execute(text(sql), params)
        except RecordNotFoundError:
            self.insert(
                InsertPlan(contract=plan.contract, row=plan.row, schema_hash=plan.schema_hash),
                backend,
            )

    def get(self, plan: ReadPlan, backend: Backend) -> dict[str, Any]:
        key_field = plan.contract.key.field
        row = backend.fetch_one(
            text(f'SELECT * FROM "{plan.contract.table_name}" WHERE "{key_field}" = :key'),
            {"key": plan.key},
        )
        if row is None:
            raise RecordNotFoundError(
                f"Record not found in {plan.contract.table_name!r} with key {plan.key!r}"
            )
        return self._row_to_payload(row._mapping)

    def delete(self, plan: DeletePlan, backend: Backend) -> None:
        key_field = plan.contract.key.field
        with backend.begin() as conn:
            conn.execute(
                text(f'DELETE FROM "{plan.contract.table_name}" WHERE "{key_field}" = :key'),
                {"key": plan.key},
            )

    def count(self, plan: CountPlan, backend: Backend) -> int:
        row = backend.fetch_one(text(f'SELECT COUNT(*) AS cnt FROM "{plan.contract.table_name}"'))
        if row is None:
            return 0
        return int(row._mapping["cnt"])

    def find(self, plan: FindPlan, backend: Backend) -> list[dict[str, Any]]:
        if not plan.filters:
            return self.all(AllPlan(contract=plan.contract), backend)
        clauses = [f'"{k}" = :{k}' for k in plan.filters]
        where = " AND ".join(clauses)
        rows = backend.fetch_all(
            text(f'SELECT * FROM "{plan.contract.table_name}" WHERE {where}'),
            dict(plan.filters),
        )
        return [self._row_to_payload(row._mapping) for row in rows]

    def all(self, plan: AllPlan, backend: Backend) -> list[dict[str, Any]]:
        query = f'SELECT * FROM "{plan.contract.table_name}"'
        if plan.limit is not None:
            query += f" LIMIT {int(plan.limit)}"
        rows = backend.fetch_all(text(query))
        return [self._row_to_payload(row._mapping) for row in rows]

    def _row_to_payload(self, mapping: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for key, value in dict(mapping).items():
            if key in METADATA_COLUMNS:
                continue
            payload[key] = value
        return payload
