# TEST_PLAN.md

# ModelVault v0.1 Test Plan

## Purpose

This document defines the required tests for ModelVault v0.1.

The tests should prove the architecture, not just code coverage.

## Test Principles

- Test public API first.
- Test contracts independently.
- Test planner without database access.
- Test backend without Pydantic awareness.
- Test collection as the integration boundary.
- Use temporary SQLite databases.
- Ensure README examples execute.

## Required Test Files

```text
tests/
  test_public_api.py
  test_model_decorator.py
  test_contracts.py
  test_fingerprints.py
  test_registry.py
  test_sqlite_backend.py
  test_table_storage.py
  test_planner.py
  test_collection_crud.py
  test_validation.py
  test_drift.py
  test_health.py
```

## Public API Tests

Verify:

- `from modelvault import Vault, model`
- `Vault.sqlite("...")`
- `vault.collection(User)`
- README example works

## Decorator Tests

Verify:

- decorator attaches config
- config includes key/storage/indexes/table_name
- decorator does not break Pydantic validation
- missing key fails during contract build

## Contract Tests

Verify:

- contract builds from decorated model
- contract builds from manual registration
- key must exist
- indexes must exist
- unsupported storage fails in v0.1
- non-Pydantic class fails

## Fingerprint Tests

Verify:

- same model gives same hash
- field addition changes hash
- key change changes hash
- index change changes hash
- ordering is deterministic

## Registry Tests

Verify:

- metadata tables are created
- contract is stored
- contract can be loaded
- list_contracts works
- drift is detected when current hash differs from stored hash

## SQLite Backend Tests

Verify:

- engine creates
- health passes
- execute works
- transactions work
- close works

## Table Storage Tests

Verify:

- SQL table is created
- simple fields map to columns
- complex fields store as JSON text
- primary key exists
- indexes are created

## Planner Tests

Verify:

- plan_insert returns InsertPlan
- plan_read returns ReadPlan
- planning has no database side effects
- plans are immutable
- invalid filters fail clearly

## Collection CRUD Tests

Verify:

- insert/get
- upsert new
- upsert existing
- delete
- exists
- count
- all
- find by equality
- missing record raises RecordNotFoundError or returns configured result

## Validation Tests

Verify:

- invalid writes fail
- invalid reads fail if database manually corrupted
- validate_all reports invalid rows
- nested model round-trip works

## Health Tests

Verify:

- healthy vault reports healthy
- missing metadata reports unhealthy
- drift reports unhealthy or warning

## Integration Scenario

Test this exact flow:

```python
@model(key="id", storage="table", indexes=["email"])
class User(BaseModel):
    id: int
    email: EmailStr
    active: bool = True

vault = Vault.sqlite(tmp_path / "app.db")
users = vault.collection(User)

users.insert(User(id=1, email="a@example.com"))
assert users.get(1).email == "a@example.com"

users.upsert(User(id=1, email="b@example.com"))
assert users.get(1).email == "b@example.com"

assert users.count() == 1
assert users.find(email="b@example.com")[0].id == 1

users.delete(1)
assert users.count() == 0
```

## Minimum Passing Bar

Before calling v0.1 complete:

- all tests pass
- README example passes
- no test requires network
- no test requires PostgreSQL/DuckDB
- all tests run using temporary SQLite
