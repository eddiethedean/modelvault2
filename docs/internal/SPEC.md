# SPEC.md

# ModelVault Technical Specification

## Purpose

This document defines the functional specification for ModelVault v0.x. It translates the architectural concepts into concrete behaviors, interfaces, and implementation requirements.

---

# Product Definition

ModelVault is a **model integrity layer** for Python applications.

It persists ordinary Pydantic models to trusted databases while guaranteeing:

- validation on write
- validation on read
- schema fingerprinting
- model registry
- drift detection
- migration planning

ModelVault is **not** a database or ORM.

---

# Public API

## Vault

```python
vault = Vault("sqlite:///app.db")
```

Required methods:

```python
collection(model)
register(model)
models()
describe(model)
health()
check()
close()
```

## Model Decorator

```python
@model(
    key="id",
    storage="hybrid",
    indexes=["email"]
)
class User(BaseModel):
    ...
```

Required options:

- key
- storage
- indexes
- table_name (optional)
- serializer (optional)

## Collection[T]

Collections expose a repository-style interface.

```python
users.insert(model)
users.upsert(model)
users.get(key)
users.delete(key)
users.exists(key)
users.count()
users.all()
users.find(**filters)
users.validate_all()
```

Collections MUST return validated model instances.

---

# Backend Interface

Every backend SHALL implement:

```python
connect()
disconnect()

ensure_schema(contract)

insert(contract, payload)
upsert(contract, payload)
get(contract, key)
delete(contract, key)

execute(statement)
health()
```

Official backends:

- SQLite (v0.1)
- PostgreSQL (v0.4)
- DuckDB (v0.5)

---

# Storage Strategies

## Table

Each model maps to one SQL table.

## Document

Entire model stored as JSON.

## Hybrid

Indexed columns + complete JSON payload.

Every strategy MUST implement:

- ensure_schema()
- insert()
- update()
- get()
- delete()
- diff()

---

# Registry

ModelVault SHALL maintain metadata tables.

Minimum required tables:

- modelvault_registry
- modelvault_schemas
- modelvault_migrations
- modelvault_validation_events

Registry MUST survive application restarts.

---

# Schema Fingerprints

Each persistence contract SHALL produce a deterministic hash.

Fingerprint inputs include:

- model fields
- types
- defaults
- storage mode
- indexes
- key field

Changing any of these MUST generate a new fingerprint.

---

# Validation Rules

Writes:

1. Coerce input
2. Validate with Pydantic
3. Serialize
4. Persist

Reads:

1. Load record
2. Deserialize
3. Validate
4. Return model

Validation is enabled by default.

---

# Health Reports

`vault.health()` SHALL report:

- backend connectivity
- metadata integrity
- schema status
- index status
- migration status
- validation status

---

# Drift Detection

ModelVault SHALL compare:

Current contract

vs

Stored contract

Outputs:

- compatible
- safe migration
- unsafe migration
- incompatible

---

# Migration Planning

Initial releases generate plans only.

Migration classes:

- Safe
- Review Required
- Unsafe

Alembic integration is deferred.

---

# Serialization

Serializer MUST support:

- nested Pydantic models
- UUID
- datetime
- Decimal
- Enum
- Path
- bytes
- Optional
- collections

Serializer MUST round-trip models without loss.

---

# Error Hierarchy

```
ModelVaultError
    BackendError
    ContractError
    ValidationError
    DriftError
    MigrationError
    StorageError
    RecordNotFound
```

---

# Package Layout

```
modelvault/
    vault.py
    collection.py
    decorators.py
    contracts.py
    registry.py
    validation.py
    serialization.py

    storage/
    backends/
    migrations/
    cli/
```

---

# Functional Requirements

FR-001 Models SHALL remain ordinary Pydantic models.

FR-002 Reads SHALL return validated models.

FR-003 Writes SHALL validate before persistence.

FR-004 Data SHALL remain accessible without ModelVault.

FR-005 Registry SHALL maintain schema history.

FR-006 Drift SHALL be detectable.

FR-007 SQLite SHALL be the first supported backend.

FR-008 SQLAlchemy Core SHALL be the primary database abstraction.

FR-009 Storage strategies SHALL be interchangeable.

FR-010 Metadata SHALL be stored in ordinary database tables.

---

# Non-Functional Requirements

- Strong typing
- Database portability
- Predictable APIs
- Minimal runtime overhead
- Explicit errors
- High test coverage
- Stable public API before 1.0

---

# Success Criteria

Version 1.0 is achieved when a developer can:

1. Define a Pydantic model.
2. Register it with ModelVault.
3. Persist and retrieve validated models.
4. Detect schema drift.
5. Generate migration plans.
6. Move between SQLite and PostgreSQL with minimal code changes.
7. Inspect model metadata directly from the database.

If these goals are met, ModelVault fulfills its mission of making model-centric persistence simple, trustworthy, and portable.
