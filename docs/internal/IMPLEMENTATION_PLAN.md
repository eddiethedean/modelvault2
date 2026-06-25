# IMPLEMENTATION_PLAN.md

# ModelVault v0.17 Implementation Plan

## Purpose

This document defines the recommended build order for Cursor or another coding agent.

The implementation must proceed from core contracts outward to storage and public API.

## Phase 0 — Project Setup

Create:

```text
pyproject.toml
src/modelvault/
tests/
```

Dependencies:

- pydantic v2
- sqlalchemy v2
- pytest

Configure:

- pytest
- ruff optional
- pyright/mypy optional

## Phase 1 — Error Types

Create `errors.py`.

Required errors:

```python
ModelVaultError
ContractError
RegistrationError
BackendError
StorageError
PlanningError
ValidationError
DriftError
RecordNotFoundError
```

## Phase 2 — Decorator Metadata

Create `decorators.py`.

Implement:

```python
@model(key="id", storage="table", indexes=None, table_name=None)
```

Attach metadata to class as:

```python
__modelvault_config__
```

Do not alter Pydantic behavior.

## Phase 3 — Contracts

Create `contracts.py`.

Implement immutable dataclasses:

- PersistenceContract
- KeyDefinition
- StorageDefinition
- IndexDefinition

Add builder:

```python
build_contract(model_type, overrides=None) -> PersistenceContract
```

Validate:

- model is Pydantic BaseModel subclass
- key exists
- storage is table for v0.17
- indexes exist as fields

## Phase 4 — Fingerprints

Create `fingerprint.py`.

Implement:

```python
fingerprint_contract(contract) -> str
```

Rules:

- deterministic JSON serialization
- sorted keys
- stable field type representation
- include algorithm version

Add tests for same model producing same hash.

## Phase 5 — Metadata Tables

Create `metadata/tables.py`.

Define SQLAlchemy Core tables:

- modelvault_registry
- modelvault_schemas
- modelvault_validation_events

## Phase 6 — SQLite Backend

Create backend protocol and SQLite backend.

Implement:

```python
SQLiteBackend.from_path(path)
execute(...)
fetch_one(...)
fetch_all(...)
begin()
close()
health()
```

Use SQLAlchemy Core engine.

## Phase 7 — Registry

Create `registry.py`.

Implement:

```python
ensure_metadata()
register_contract(contract)
get_contract(collection_name)
list_contracts()
detect_drift(contract)
```

Store contract metadata and schema JSON.

## Phase 8 — Serialization

Create `serialization.py`.

Implement:

```python
serialize_model(model, contract) -> dict
deserialize_payload(payload, model_type) -> dict
```

Handle:

- UUID
- datetime/date
- Decimal
- Enum
- list/dict/nested models as JSON

## Phase 9 — Validation

Create `validation.py`.

Implement:

```python
validate_write(model_or_dict, model_type)
validate_read(payload, model_type)
validate_many(payloads, model_type)
```

## Phase 10 — Plans

Create `plans.py`.

Implement immutable dataclasses:

- InsertPlan
- ReadPlan
- UpsertPlan
- DeletePlan
- CountPlan
- FindPlan
- ValidateAllPlan

## Phase 11 — Planner

Create `planner.py`.

Implement:

```python
plan_insert(contract, model)
plan_read(contract, key)
plan_upsert(contract, model)
plan_delete(contract, key)
plan_count(contract)
plan_find(contract, filters)
plan_validate_all(contract)
```

No database access.

## Phase 12 — Table Storage

Create `storage/table.py`.

Implement:

```python
ensure_schema(contract, backend)
insert(plan, backend)
upsert(plan, backend)
get(plan, backend)
delete(plan, backend)
count(plan, backend)
find(plan, backend)
```

Map simple fields to SQL columns. Store complex fields as JSON text.

## Phase 13 — Collection

Create `collection.py`.

Implement public methods:

- insert
- upsert
- get
- delete
- exists
- count
- all
- find
- validate_all

Collection coordinates:

```text
validate -> plan -> storage -> backend -> deserialize -> validate
```

## Phase 14 — Vault

Create `vault.py`.

Implement:

```python
Vault(url)
Vault.sqlite(path)
register(model)
collection(model)
models()
describe(model)
health()
close()
```

## Phase 15 — Integration Tests

Test full lifecycle:

- create vault
- register model
- create collection
- insert
- get
- upsert
- find
- delete
- count
- drift detection

## Phase 16 — Documentation Examples

Ensure README examples run.

## Implementation Rule

Do not add v0.18 features during v0.17 implementation.

No hybrid storage, document storage, PostgreSQL, DuckDB, Alembic, async, plugins, or complex query DSL.
