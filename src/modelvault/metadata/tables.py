"""SQLAlchemy Core definitions for ModelVault metadata tables."""

from __future__ import annotations

from sqlalchemy import Column, Integer, MetaData, Table, Text

metadata = MetaData()

registry_table = Table(
    "modelvault_registry",
    metadata,
    Column("collection_name", Text, primary_key=True),
    Column("model_name", Text, nullable=False),
    Column("python_path", Text, nullable=False),
    Column("table_name", Text, nullable=False),
    Column("storage_mode", Text, nullable=False),
    Column("key_field", Text, nullable=False),
    Column("contract_hash", Text, nullable=False),
    Column("created_at", Text, nullable=False),
    Column("updated_at", Text, nullable=False),
)

schemas_table = Table(
    "modelvault_schemas",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("collection_name", Text, nullable=False),
    Column("contract_hash", Text, nullable=False),
    Column("schema_json", Text, nullable=False),
    Column("modelvault_version", Text, nullable=False),
    Column("fingerprint_version", Text, nullable=False),
    Column("created_at", Text, nullable=False),
)

validation_events_table = Table(
    "modelvault_validation_events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("collection_name", Text, nullable=False),
    Column("record_key", Text, nullable=True),
    Column("direction", Text, nullable=False),
    Column("status", Text, nullable=False),
    Column("error_json", Text, nullable=True),
    Column("created_at", Text, nullable=False),
)
