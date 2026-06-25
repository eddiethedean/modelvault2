# STORAGE.md

# Storage Architecture

## Purpose

This document defines v0.1 storage behavior.

ModelVault storage strategies translate Persistence Contracts and Execution Plans into backend operations.

v0.1 supports only **Table Storage**.

## Storage Strategy Role

A Storage Strategy is responsible for physical representation.

It knows:

- how to create tables
- how to map fields to columns
- how to prepare inserts
- how to reconstruct payloads from rows

It does not know:

- how to validate Pydantic models
- how to compute fingerprints
- how to store registry metadata
- how to manage database connections

## v0.1 Table Storage

Each model maps to one SQL table.

Example model:

```python
@model(key="id", storage="table", indexes=["email"])
class User(BaseModel):
    id: int
    email: EmailStr
    active: bool = True
```

Generated table:

```text
users
  id INTEGER PRIMARY KEY
  email TEXT NOT NULL
  active BOOLEAN NOT NULL
```

## Table Naming

Default table name:

- snake_case plural-ish model name is acceptable
- simpler v0.1 default: lowercase model name + "s"

Examples:

```text
User -> users
AuditEvent -> auditevents
```

Allow override:

```python
@model(key="id", storage="table", table_name="app_users")
```

## Type Mapping

v0.1 type mapping:

| Python/Pydantic Type | SQLite Type |
|---|---|
| str | TEXT |
| int | INTEGER |
| float | REAL |
| bool | BOOLEAN |
| datetime | TEXT |
| date | TEXT |
| UUID | TEXT |
| Decimal | TEXT |
| Enum | TEXT |
| list | TEXT JSON |
| dict | TEXT JSON |
| nested BaseModel | TEXT JSON |
| Optional[T] | nullable mapped type |

## Required vs Nullable

Required fields should be NOT NULL unless they have Optional type.

Optional fields should allow NULL.

Fields with defaults may be NOT NULL if default is always materialized during serialization.

## Primary Key

The contract key becomes the SQL primary key.

v0.1 supports single-column keys only.

## Indexes

Indexes are declared in the contract.

```python
@model(key="id", storage="table", indexes=["email"])
```

v0.1 supports simple single-field non-unique indexes.

## Complex Fields

Complex fields are serialized to JSON text.

Examples:

- dict
- list
- nested Pydantic model
- arbitrary structured values

## Metadata Columns

For v0.1, application tables should include:

```text
__modelvault_schema_hash TEXT
__modelvault_created_at TEXT
__modelvault_updated_at TEXT
```

These columns help validate records and support future migrations.

## Storage Interface

Expected methods:

```python
ensure_schema(contract, backend)
insert(plan, backend)
upsert(plan, backend)
get(plan, backend)
delete(plan, backend)
count(plan, backend)
find(plan, backend)
all(plan, backend)
```

## Storage Invariants

- Storage never validates Pydantic models.
- Storage never computes contract hashes.
- Storage never mutates registry metadata directly.
- Storage always uses backend abstraction.
- Storage never opens raw database connections.
