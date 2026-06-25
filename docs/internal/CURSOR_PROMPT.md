# CURSOR_PROMPT.md

# Cursor Implementation Prompt

Use this prompt to ask Cursor to implement ModelVault v0.17.

---

You are implementing ModelVault v0.17 from the design documents in this repository.

ModelVault is a Model Integrity Platform for Python. It is not a database and not a traditional ORM. It persists ordinary Pydantic v2 models into trusted databases, starting with SQLite through SQLAlchemy Core.

## Required Reading

Before coding, read these docs:

1. README.md
2. VISION.md
3. CORE_CONCEPTS.md
4. DESIGN_PRINCIPLES.md
5. CONTRACTS.md
6. MVP_SPEC.md
7. PACKAGE_STRUCTURE.md
8. IMPLEMENTATION_PLAN.md
9. STORAGE.md
10. REGISTRY.md
11. SQLITE_BACKEND.md
12. TEST_PLAN.md
13. EXECUTION_PLANNER.md

## Hard Constraints

Do not implement out-of-scope features.

Do NOT implement:

- PostgreSQL
- DuckDB
- async API
- hybrid storage
- document storage
- Alembic integration
- plugins
- relationships
- joins
- complex query DSL
- custom database engine

Implement only v0.17.

## Architecture Rules

- Models remain ordinary Pydantic models.
- Persistence Contracts are immutable.
- Planner produces immutable plans.
- Planner never touches the database.
- Backend never imports or understands Pydantic.
- Collection never writes raw SQL directly.
- Storage strategy maps plans to backend operations.
- Registry stores metadata but does not perform application CRUD.
- SQLite storage uses SQLAlchemy Core.

## Build Order

Follow IMPLEMENTATION_PLAN.md exactly.

Start with:

1. pyproject.toml
2. package structure
3. errors.py
4. decorators.py
5. contracts.py
6. fingerprint.py
7. metadata tables
8. SQLite backend
9. registry
10. serialization
11. validation
12. plans
13. planner
14. table storage
15. collection
16. vault
17. tests

## Required Public API

```python
from modelvault import Vault, model
```

Example must work:

```python
from pydantic import BaseModel, EmailStr
from modelvault import Vault, model

@model(key="id", storage="table", indexes=["email"])
class User(BaseModel):
    id: int
    email: EmailStr
    active: bool = True

vault = Vault.sqlite("app.db")
users = vault.collection(User)

users.insert(User(id=1, email="alice@example.com"))

loaded = users.get(1)

assert loaded.email == "alice@example.com"
```

## Testing

Implement tests from TEST_PLAN.md.

All tests must use temporary SQLite files.

No network services.

No PostgreSQL.

No DuckDB.

## Completion Criteria

v0.17 is complete when:

- README example works
- all tests pass
- metadata tables are created
- model tables are created
- insert/get/upsert/delete/count/find work
- read/write validation works
- contract hash is deterministic
- drift detection works

Do not expand scope.
