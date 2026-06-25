# MVP_SPEC.md

# ModelVault v0.1 MVP Specification

## Purpose

This document defines the exact scope of ModelVault v0.1.

The goal of v0.1 is not to build the full ModelVault vision. The goal is to prove the core architecture:

> A Pydantic model can be converted into a Persistence Contract, registered in database metadata, planned into execution operations, stored in SQLite, and read back as a validated model.

## v0.1 Product Statement

ModelVault v0.1 is a SQLite-backed model integrity layer for ordinary Pydantic v2 models.

It supports:

- Pydantic model contracts
- SQLite through SQLAlchemy Core
- table storage
- typed collections
- insert/get/upsert/delete/exists/count
- validation on write
- validation on read
- metadata registry tables
- deterministic contract fingerprints
- basic health check
- basic drift detection

It does not support the full long-term vision yet.

## Primary User Story

As a Python developer, I want to define a Pydantic model, register it with ModelVault, and persist validated records into SQLite without creating a separate ORM model.

```python
from pydantic import BaseModel, EmailStr
from modelvault import Vault, model

@model(key="id", storage="table")
class User(BaseModel):
    id: int
    email: EmailStr
    active: bool = True

vault = Vault.sqlite("app.db")
users = vault.collection(User)

users.insert(User(id=1, email="alice@example.com"))
loaded = users.get(1)

assert isinstance(loaded, User)
assert loaded.email == "alice@example.com"
```

## Included in v0.1

### Public API

Required:

```python
from modelvault import Vault, model
```

Required methods:

```python
Vault.sqlite(path)
Vault(url)
vault.register(model, **options)
vault.collection(model)
vault.models()
vault.describe(model)
vault.health()
vault.close()
```

Collection methods:

```python
insert(model)
upsert(model)
get(key)
delete(key)
exists(key)
count()
all(limit=None)
find(**filters)
validate_all()
```

### Pydantic Support

v0.1 supports Pydantic v2 `BaseModel`.

Required field types:

- str
- int
- float
- bool
- datetime
- date
- UUID
- Decimal
- Enum
- Optional
- list/dict serialized as JSON text
- nested BaseModel serialized as JSON text

### Storage

v0.1 supports **table storage only**.

Each model gets one SQL table.

Complex fields are stored as JSON text columns.

### Backend

v0.1 supports SQLite via SQLAlchemy Core.

### Registry

v0.1 creates ModelVault metadata tables:

- modelvault_registry
- modelvault_schemas
- modelvault_validation_events

### Fingerprints

v0.1 computes deterministic contract hashes from:

- model name
- model module
- fields
- field types
- required/optional status
- default presence
- key field
- storage mode
- indexes

### Validation

Required:

- validate on insert
- validate on upsert
- validate on get
- validate on all/find
- collect errors during validate_all

### Planner

v0.1 includes a simple Planner with:

- InsertPlan
- ReadPlan
- UpsertPlan
- DeletePlan
- CountPlan
- FindPlan
- ValidateAllPlan

### CLI

Optional in v0.1. Do not prioritize until the library API is stable.

## Excluded from v0.1

Do not implement:

- PostgreSQL
- DuckDB
- async API
- document storage
- hybrid storage
- Alembic integration
- automatic migrations
- custom plugin system
- encryption
- cache layer
- multi-tenancy
- relationships/foreign keys
- joins
- query DSL
- schema-altering migrations beyond initial table creation
- multiple contracts per model
- full CLI
- Pandas/Polars/Arrow integrations

## v0.1 Success Criteria

v0.1 is complete when:

1. A user can define a Pydantic model.
2. A user can register the model with a key field.
3. ModelVault creates metadata tables.
4. ModelVault creates a SQLite table for the model.
5. Insert validates and persists the model.
6. Get reads, deserializes, validates, and returns the model.
7. Upsert works.
8. Delete works.
9. Count works.
10. Find by simple equality works.
11. Contract metadata is stored.
12. Contract hash is deterministic.
13. Drift is detected when the model changes.
14. Unit tests cover the full path.

## MVP Invariants

- Models remain ordinary Pydantic models.
- SQLite owns storage.
- SQLAlchemy Core owns SQL construction.
- ModelVault validates read/write boundaries.
- Collection never writes raw SQL directly.
- Backend never imports Pydantic.
- Planner never executes database operations.
- Registry never performs application CRUD.
