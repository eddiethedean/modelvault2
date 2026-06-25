# ARCHITECTURE.md

# ModelVault Architecture

## Purpose

This document defines the proposed architecture for the redesigned ModelVault package.

ModelVault is a **model integrity layer** between Pydantic and trusted databases. It provides typed model persistence, validation, schema tracking, drift detection, and migration intelligence while delegating durable storage to established database systems such as SQLite, PostgreSQL, and DuckDB.

ModelVault should be boring underneath and opinionated above.

```text
Application Code
      ↓
Pydantic Models
      ↓
ModelVault Contracts
      ↓
Collections
      ↓
Backends
      ↓
SQLite / PostgreSQL / DuckDB
```

---

# Architectural Goals

ModelVault should:

1. Persist ordinary Pydantic models without requiring ORM-specific base classes.
2. Validate models before writes.
3. Validate records after reads.
4. Track schema fingerprints in database metadata.
5. Detect drift between current model contracts and stored contracts.
6. Support multiple storage strategies per model.
7. Use trusted databases for durability, transactions, indexing, and recovery.
8. Keep data accessible without ModelVault.
9. Integrate with SQLAlchemy and Alembic instead of replacing them.
10. Provide a clear typed repository API.

---

# Non-Goals

ModelVault should not:

1. Implement a custom database engine.
2. Implement transaction logic itself.
3. Replace SQLAlchemy.
4. Replace Alembic.
5. Hide SQL from advanced users.
6. Force users to rewrite domain models as ORM models.
7. Require proprietary storage formats.
8. Become a general-purpose ORM.

---

# High-Level Architecture

```text
┌──────────────────────────────────────────────┐
│                Application                   │
│  FastAPI / CLI / Scripts / Services / Jobs   │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────┐
│              Pydantic Models                 │
│        User, Order, Event, Config            │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────┐
│          Persistence Contracts               │
│ key, storage mode, indexes, version policy   │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────┐
│                 Vault                        │
│ registry, collections, health, migrations    │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────┐
│               Collections                    │
│ typed CRUD, validation, import/export        │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────┐
│           Storage Strategies                 │
│ table / document / hybrid                    │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────┐
│                 Backends                     │
│ SQLAlchemy / DuckDB                          │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────┐
│            Trusted Databases                 │
│ SQLite / PostgreSQL / DuckDB                 │
└──────────────────────────────────────────────┘
```

---

# Primary Runtime Objects

## Vault

The `Vault` is the root coordinator.

```python
vault = Vault("sqlite:///app.db")
```

Responsibilities:

- create and manage backend connections
- initialize metadata tables
- register model contracts
- create collections
- expose health checks
- expose schema inspection
- coordinate migration planning
- provide import/export entry points

The Vault should be lightweight. It should not hold long-lived application state beyond backend and registry handles.

## Persistence Contract

A `PersistenceContract` is the normalized internal representation of a model's persistence rules.

A contract is created from a decorator or explicit registration.

```python
@model(key="id", storage="hybrid", indexes=["email"])
class User(BaseModel):
    id: UUID
    email: EmailStr
```

Contract fields:

```text
model_name
model_type
python_path
key_field
storage_mode
indexes
schema_json
schema_hash
serializer
version_policy
backend_requirements
created_at
```

The contract is the canonical input to storage strategy compilation.

## Collection

A `Collection[T]` is a typed repository for a model.

```python
users = vault.collection(User)
```

Responsibilities:

- typed CRUD
- write validation
- read validation
- query helpers
- bulk operations
- validation reports
- import/export
- strategy dispatch

A collection should not know SQL dialect details. It talks to a storage strategy and backend interface.

## Registry

The Registry manages metadata about models and contracts.

Responsibilities:

- store contract metadata
- track schema versions
- detect drift
- report status
- record migrations
- record validation events
- expose introspection APIs

The Registry is both:

1. a runtime service, and
2. persisted database metadata.

## Backend

A Backend adapts ModelVault to a concrete database technology.

Examples:

- `SQLAlchemyBackend`
- `SQLiteBackend`
- `PostgresBackend`
- `DuckDBBackend`

Responsibilities:

- connections
- transactions
- SQL execution
- table creation
- index creation
- dialect capabilities
- row/document read/write operations

Backends should not perform Pydantic validation.

## Storage Strategy

A Storage Strategy determines how a model is physically represented.

Strategies:

- `TableStorage`
- `DocumentStorage`
- `HybridStorage`

Responsibilities:

- compile contract to physical schema
- serialize model data into backend operations
- deserialize backend records into model payloads
- produce migration diffs
- define queryable fields
- define indexes

---

# Layered Design

## Layer 1: Public API

The public API should be small.

```python
from modelvault import Vault, model
```

Core public objects:

```text
Vault
Collection
model decorator
StorageMode
ValidationReport
HealthReport
MigrationPlan
```

The first stable API should avoid exposing unnecessary internals.

## Layer 2: Contract Layer

The contract layer converts user model declarations into normalized internal metadata.

Modules:

```text
contracts.py
decorators.py
schema.py
fingerprint.py
```

Key outputs:

```text
PersistenceContract
SchemaFingerprint
IndexDefinition
StorageDefinition
```

## Layer 3: Collection Layer

The collection layer provides typed operations.

Modules:

```text
collection.py
query.py
bulk.py
validation.py
```

The collection layer calls:

- serializer
- validator
- storage strategy
- backend

It never directly emits backend-specific SQL.

## Layer 4: Storage Strategy Layer

The strategy layer maps contracts to physical representation.

Modules:

```text
storage/table.py
storage/document.py
storage/hybrid.py
```

Each strategy implements the same protocol:

```python
class StorageStrategy(Protocol):
    def ensure_schema(self, contract, backend): ...
    def insert(self, model, contract, backend): ...
    def upsert(self, model, contract, backend): ...
    def get(self, key, contract, backend): ...
    def delete(self, key, contract, backend): ...
    def diff(self, contract, registry_state, backend): ...
```

## Layer 5: Backend Layer

The backend layer is responsible for database mechanics.

Modules:

```text
backends/base.py
backends/sqlalchemy.py
backends/sqlite.py
backends/postgres.py
backends/duckdb.py
```

The SQLAlchemy backend should be the main v0.17 implementation. SQLite should ride on SQLAlchemy first.

DuckDB may have both:

- SQLAlchemy dialect support, and/or
- direct native support

depending on reliability and feature needs.

## Layer 6: Registry and Metadata Layer

The registry layer persists ModelVault metadata in the target database.

Modules:

```text
registry.py
metadata.py
migrations/history.py
```

It should be database-native and inspectable.

## Layer 7: CLI Layer

The CLI wraps architecture features for operational use.

Modules:

```text
cli/main.py
cli/check.py
cli/inspect.py
cli/diff.py
cli/validate.py
```

---

# Metadata Architecture

ModelVault stores metadata in ordinary database tables.

Metadata should be:

- minimal
- readable
- versioned
- backend-portable
- safe to inspect manually

## Proposed Metadata Tables

### modelvault_registry

Stores registered collections.

```text
collection_name
model_name
python_path
table_name
storage_mode
key_field
current_schema_hash
created_at
updated_at
```

### modelvault_schemas

Stores historical schema fingerprints.

```text
schema_hash
collection_name
model_name
schema_json
pydantic_version
modelvault_version
created_at
```

### modelvault_migrations

Stores migration history.

```text
migration_id
collection_name
from_schema_hash
to_schema_hash
status
applied_at
details_json
```

### modelvault_validation_events

Stores validation failures or audit events.

```text
event_id
collection_name
record_key
direction
status
error_json
created_at
```

### modelvault_indexes

Stores index expectations.

```text
collection_name
index_name
fields_json
unique
status
created_at
```

---

# Data Flow Architecture

## Write Flow

```text
User object or dict
        ↓
Collection.insert()
        ↓
Coerce to Pydantic model
        ↓
Validate
        ↓
Serialize
        ↓
Storage strategy maps to physical representation
        ↓
Backend transaction
        ↓
Metadata/update events if needed
```

Example:

```python
users.insert(User(id=1, email="odos@example.com"))
```

Responsibilities by layer:

```text
Collection        validates and coordinates
Serializer        converts model to backend payload
StorageStrategy   maps payload to row/document/hybrid representation
Backend           executes transaction
Registry          records metadata if needed
```

## Read Flow

```text
Collection.get(key)
        ↓
Storage strategy requests backend record
        ↓
Backend returns row/document
        ↓
Storage strategy reconstructs model payload
        ↓
Pydantic validates payload
        ↓
Collection returns model instance
```

Read validation is required by default.

Optional modes may exist later:

```python
users.get(key, validate=False)
users.get(key, validation="warn")
```

But the default should preserve ModelVault's integrity promise.

## Registration Flow

```text
User defines Pydantic model
        ↓
User applies @model decorator or registers manually
        ↓
Contract builder extracts schema
        ↓
Fingerprint generated
        ↓
Vault compares registry state
        ↓
Storage strategy ensures schema
        ↓
Registry metadata written
```

## Health Check Flow

```text
vault.health()
        ↓
backend connectivity check
        ↓
metadata table check
        ↓
registered model import check
        ↓
schema fingerprint check
        ↓
storage object check
        ↓
index check
        ↓
optional validation scan
        ↓
HealthReport
```

## Drift Detection Flow

```text
Current model contract
        ↓
Stored registry contract
        ↓
Compare fingerprints
        ↓
Compare fields/indexes/storage rules
        ↓
Generate DriftReport
        ↓
Suggest migration plan
```

---

# Storage Strategy Architecture

## Table Storage

Table storage maps model fields to SQL columns.

Best for:

- simple models
- relational querying
- strong schema enforcement
- BI tools
- production tables

Limitations:

- nested models require flattening or JSON fields
- migrations can be more complex
- not ideal for highly variable data

## Document Storage

Document storage stores the entire model as JSON.

Best for:

- nested Pydantic models
- audit events
- flexible records
- logs
- evolving schemas

Limitations:

- fewer native relational guarantees
- limited queryability unless indexed fields are extracted
- backend JSON support varies

## Hybrid Storage

Hybrid storage stores selected fields as columns and the full validated model as JSON.

Best for:

- most application models
- nested data with queryable fields
- schema evolution
- model round-tripping
- practical SQL access

Hybrid storage is likely the default recommendation for early ModelVault applications.

---

# Backend Architecture

## SQLAlchemy Backend

The SQLAlchemy backend should be the foundational backend.

It provides:

- SQLite support
- PostgreSQL support
- broad dialect support
- connection lifecycle
- transactions
- DDL generation
- SQL expression support

ModelVault should use SQLAlchemy Core first, not the ORM.

Reason:

- ModelVault already has its own model abstraction.
- SQLAlchemy ORM would introduce another model layer.
- SQLAlchemy Core is better suited for generated tables and metadata operations.

## SQLite

SQLite should be the v0.17 backend.

It is ideal for:

- local development
- tests
- examples
- desktop apps
- single-file persistence

## PostgreSQL

PostgreSQL should be the primary production target.

It enables:

- JSONB
- robust indexing
- concurrency
- operational maturity
- migration tooling

## DuckDB

DuckDB should be the analytics backend.

It enables:

- local analytical workloads
- model collections as datasets
- Parquet import/export
- notebooks
- experiment tracking

DuckDB should not block the initial architecture. It can be added after the SQLAlchemy + SQLite path is solid.

---

# Serialization Architecture

Serialization converts models into backend-safe payloads.

Responsibilities:

- convert Pydantic models to Python primitives
- handle UUID, datetime, Decimal, Enum, Path, bytes, nested models
- preserve enough information for round-tripping
- support backend-specific JSON capabilities
- optionally support custom field serializers

Default serializer should use Pydantic v2 mechanisms where possible.

Potential API:

```python
@model(serializer=CustomSerializer())
class User(BaseModel):
    ...
```

or:

```python
vault = Vault("sqlite:///app.db", serializer=DefaultSerializer())
```

---

# Validation Architecture

Validation is a first-class layer.

Types of validation:

1. write validation
2. read validation
3. bulk validation
4. migration validation
5. registry validation
6. health-check validation

Default policy:

```text
Writes must validate.
Reads must validate.
Bulk validation can collect errors.
Health validation can sample or scan.
```

Potential policy options:

```python
vault = Vault(
    "sqlite:///app.db",
    validation="strict",
)
```

Modes:

```text
strict     raise on validation error
warn       return model when possible and log warning
report     collect errors in ValidationReport
disabled   internal/testing only
```

---

# Migration Architecture

ModelVault should not replace Alembic.

Instead, it should produce model-aware migration intelligence.

Responsibilities:

- compare schema fingerprints
- classify changes
- generate migration plans
- identify safe vs unsafe changes
- update registry metadata
- optionally integrate with Alembic

Migration categories:

```text
safe:
  add nullable field
  add field with default
  add index

possibly unsafe:
  rename field
  change type
  remove field

unsafe:
  narrow type
  remove required field
  change key field
```

Potential commands:

```bash
modelvault diff
modelvault plan-migration
modelvault alembic revision
```

---

# Query Architecture

ModelVault should avoid becoming a full query language.

Initial query API should be intentionally small:

```python
users.get(key)
users.find(email="odos@example.com")
users.all(limit=100)
users.count()
```

Advanced users should be able to access backend-native query tools.

Possible escape hatch:

```python
users.table
users.backend
users.select()
```

Principle:

> ModelVault should simplify common model-centric queries without hiding the underlying database from advanced users.

---

# Plugin Architecture

Plugins are not required for v0.17 but should be anticipated.

Potential plugins:

- auditing
- encryption
- soft delete
- multi-tenancy
- version history
- caching
- full-text search
- event publishing
- validation logging

Plugin hooks:

```text
before_validate
after_validate
before_insert
after_insert
before_update
after_update
before_delete
after_delete
after_load
on_validation_error
on_migration
```

Plugins should operate at the collection/contract level, not at the backend level where possible.

---

# Error Architecture

Errors should be explicit and structured.

Potential error hierarchy:

```text
ModelVaultError
  ContractError
  RegistrationError
  BackendError
  StorageStrategyError
  ValidationError
  DriftDetectedError
  MigrationRequiredError
  RecordNotFoundError
  IntegrityError
```

Validation errors should preserve Pydantic error details.

---

# Proposed Package Structure

```text
modelvault/
  pyproject.toml
  README.md
  docs/
    README.md
    VISION.md
    CORE_CONCEPTS.md
    ARCHITECTURE.md
  src/
    modelvault/
      __init__.py
      vault.py
      collection.py
      decorators.py
      contracts.py
      registry.py
      metadata.py
      fingerprint.py
      validation.py
      serialization.py
      errors.py
      reports.py
      query.py

      backends/
        __init__.py
        base.py
        sqlalchemy.py
        sqlite.py
        postgres.py
        duckdb.py

      storage/
        __init__.py
        base.py
        table.py
        document.py
        hybrid.py

      migrations/
        __init__.py
        diff.py
        planner.py
        alembic.py
        history.py

      cli/
        __init__.py
        main.py
        check.py
        inspect.py
        diff.py
        validate.py

      plugins/
        __init__.py
        base.py

  tests/
    test_vault.py
    test_contracts.py
    test_collection.py
    test_registry.py
    test_sqlite_backend.py
    test_table_storage.py
    test_document_storage.py
    test_hybrid_storage.py
    test_validation.py
    test_drift.py
```

---

# v0.17 Architecture Slice

The first implementation should be intentionally narrow.

## Include

- Pydantic v2
- SQLite via SQLAlchemy Core
- Vault
- model decorator
- PersistenceContract
- Collection
- Registry metadata tables
- Table storage
- Basic CRUD
- Write validation
- Read validation
- Basic health check

## Exclude

- PostgreSQL
- DuckDB
- async
- plugin system
- Alembic integration
- complex query DSL
- automatic unsafe migrations
- full import/export
- encryption
- caching

## v0.17 Success Criteria

A user can write:

```python
@model(key="id", storage="table")
class User(BaseModel):
    id: int
    email: EmailStr

vault = Vault("sqlite:///app.db")
users = vault.collection(User)

users.insert(User(id=1, email="odos@example.com"))
loaded = users.get(1)

assert isinstance(loaded, User)
```

And ModelVault will:

1. create metadata tables
2. create the `users` table
3. validate on insert
4. store the record in SQLite
5. load the record
6. validate on read
7. return a `User`

---

# Architectural Risks

## Risk: Becoming an ORM

Mitigation:

- keep Collection API small
- use SQLAlchemy Core internally
- provide escape hatches
- focus on model lifecycle, not query abstraction

## Risk: Overcomplicated Storage Modes

Mitigation:

- implement table mode first
- add document and hybrid after the contract layer is stable
- document when each mode should be used

## Risk: Migration Complexity

Mitigation:

- start with detection and reporting
- generate migration plans before applying migrations
- integrate with Alembic later

## Risk: Backend Abstraction Leaks

Mitigation:

- expose backend capabilities explicitly
- avoid pretending every backend supports every feature
- provide clear compatibility matrix

## Risk: Validation Performance

Mitigation:

- allow configurable validation policies
- support bulk validation reports
- optimize common paths
- document performance tradeoffs

---

# Architectural North Star

ModelVault should always be judged against this question:

> Does this make application models more trustworthy while keeping storage grounded in databases users already trust?

If the answer is yes, the feature may belong.

If the answer is no, it probably does not.
