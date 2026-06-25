# SQLITE_BACKEND.md

# SQLite Backend

## Purpose

SQLite is the first supported ModelVault backend.

It provides the v0.1 proof that ModelVault can persist Pydantic models to a trusted database without inventing storage.

## Backend Role

The SQLite backend owns:

- SQLAlchemy engine creation
- connections
- transactions
- SQL execution
- table inspection
- health checks

It does not own:

- Pydantic validation
- contract building
- fingerprinting
- registry policy
- storage strategy rules

## Implementation

Use SQLAlchemy Core.

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///app.db")
```

## Construction

Public:

```python
vault = Vault.sqlite("app.db")
```

Internal:

```python
SQLiteBackend(path="app.db")
```

## Required Methods

```python
execute(statement, parameters=None)
fetch_one(statement, parameters=None)
fetch_all(statement, parameters=None)
begin()
close()
health()
table_exists(name)
```

## Transactions

Use SQLAlchemy transaction contexts.

Write operations should occur inside transactions.

## Health Check

SQLite backend health should verify:

- engine can connect
- simple SELECT works
- metadata tables are reachable if initialized

## Type Notes

SQLite has dynamic typing. ModelVault must enforce integrity at the model layer.

This reinforces the importance of read validation.

## SQLite Invariants

- Do not use raw sqlite3 directly in v0.1.
- Use SQLAlchemy Core.
- Do not validate Pydantic models in backend.
- Do not compute contracts in backend.
- Do not implement custom locking.
- Let SQLite own persistence behavior.
