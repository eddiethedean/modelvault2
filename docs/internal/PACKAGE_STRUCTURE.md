# PACKAGE_STRUCTURE.md

# ModelVault Package Structure

## Purpose

This document defines the initial Python package layout for ModelVault v0.1.

The package should be small, explicit, and implementation-friendly. Avoid premature modularity, but keep architectural boundaries clear.

## Root Layout

```text
modelvault/
  pyproject.toml
  README.md
  docs/
  src/
    modelvault/
  tests/
```

## Source Layout

```text
src/modelvault/
  __init__.py

  vault.py
  collection.py
  decorators.py

  contracts.py
  fingerprint.py
  registry.py

  planner.py
  plans.py

  serialization.py
  validation.py
  reports.py
  errors.py

  storage/
    __init__.py
    base.py
    table.py

  backends/
    __init__.py
    base.py
    sqlalchemy.py
    sqlite.py

  metadata/
    __init__.py
    tables.py

  typing.py
```

## Public API

`src/modelvault/__init__.py` should expose:

```python
from modelvault.vault import Vault
from modelvault.decorators import model
from modelvault.errors import ModelVaultError
```

Do not expose internal planner, registry, storage, or backend classes yet unless tests require them.

## Module Responsibilities

### vault.py

Owns the `Vault` class.

Responsibilities:

- backend creation
- registry creation
- model registration
- collection creation
- health check coordination
- close/dispose lifecycle

### collection.py

Owns `Collection[T]`.

Responsibilities:

- public CRUD API
- invokes planner
- invokes validator/serializer as needed
- delegates execution to backend/storage
- returns typed Pydantic models

### decorators.py

Owns `@model`.

Responsibilities:

- attach persistence metadata to Pydantic classes
- avoid mutating Pydantic behavior
- support later registration by Vault

### contracts.py

Owns core contract data structures.

Classes:

- PersistenceContract
- KeyDefinition
- StorageDefinition
- IndexDefinition
- ValidationDefinition

### fingerprint.py

Owns deterministic contract hashing.

Responsibilities:

- normalize contract payloads
- compute stable hashes
- version fingerprint algorithm

### registry.py

Owns registry runtime service.

Responsibilities:

- ensure metadata tables
- save contracts
- load contracts
- list models
- detect basic drift

### planner.py

Owns Planner.

Responsibilities:

- produce immutable plans
- no database access
- no validation execution
- no SQL execution

### plans.py

Owns execution plan dataclasses.

Classes:

- InsertPlan
- ReadPlan
- UpsertPlan
- DeletePlan
- CountPlan
- FindPlan
- ValidateAllPlan

### serialization.py

Owns serialization/deserialization.

Responsibilities:

- Pydantic model dump
- convert Python values to database-safe values
- convert database values back to model payloads

### validation.py

Owns validation service.

Responsibilities:

- validate on write
- validate on read
- collect validation errors
- return ValidationReport

### reports.py

Owns structured report types.

Classes:

- HealthReport
- ValidationReport
- DriftReport
- CollectionDescription

### errors.py

Owns error hierarchy.

### storage/base.py

Defines StorageStrategy protocol.

### storage/table.py

Implements TableStorage.

Responsibilities:

- map contract to SQLAlchemy table
- prepare insert payloads
- reconstruct payloads from rows

### backends/base.py

Defines Backend protocol.

### backends/sqlalchemy.py

Implements SQLAlchemy Core backend helpers.

### backends/sqlite.py

Implements SQLite backend.

### metadata/tables.py

Defines metadata table schemas.

## Tests Layout

```text
tests/
  test_public_api.py
  test_model_decorator.py
  test_contracts.py
  test_fingerprints.py
  test_registry.py
  test_table_storage.py
  test_sqlite_backend.py
  test_collection_crud.py
  test_validation.py
  test_drift.py
  test_health.py
```

## v0.1 Dependency Policy

Required dependencies:

- pydantic >= 2
- sqlalchemy >= 2
- typing_extensions if needed
- pytest for tests

Avoid:

- Alembic in v0.1
- DuckDB in v0.1
- async SQLAlchemy in v0.1
- optional dataframe dependencies in v0.1
