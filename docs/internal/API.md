# API.md

# ModelVault Public API Specification

## Design Goals

The public API should be:

- Pydantic-first
- strongly typed
- repository-oriented
- backend agnostic
- explicit over magical
- easy to learn in under 15 minutes

The API should hide persistence complexity without hiding the underlying database.

---

# Primary API

ModelVault intentionally exposes very few top-level objects.

```python
from modelvault import (
    Vault,
    model,
    StorageMode,
    ValidationMode,
)
```

Everything else hangs off a `Vault`.

---

# Creating a Vault

```python
from modelvault import Vault

vault = Vault("sqlite:///app.db")
```

Alternative constructors:

```python
Vault.sqlite("app.db")
Vault.postgres("postgresql+psycopg://...")
Vault.duckdb("analytics.duckdb")
```

Configuration:

```python
vault = Vault(
    url="sqlite:///app.db",
    echo=False,
    validation="strict",
    auto_create=True,
)
```

## Vault API

```python
vault.register(User)
vault.collection(User)

vault.models()
vault.describe(User)
vault.status(User)

vault.health()
vault.check()
vault.close()
```

Future:

```python
vault.diff(User)
vault.plan_migration(User)
vault.export_metadata()
```

---

# Model Registration

ModelVault does not replace Pydantic.

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    email: str
```

Persistence is added with a decorator.

```python
from modelvault import model

@model(
    key="id",
    storage="hybrid",
    indexes=["email"],
)
class User(BaseModel):
    ...
```

Or registered later:

```python
vault.register(
    User,
    key="id",
    storage="table",
)
```

Decorator metadata should remain lightweight and persistence-focused.

---

# Collections

Collections are the primary interface developers use.

```python
users = vault.collection(User)
```

Type:

```python
Collection[User]
```

## CRUD

```python
users.insert(user)
users.upsert(user)

user = users.get(1)

users.delete(1)

users.exists(1)

users.count()
```

## Queries

Simple query API:

```python
users.find(email="alice@example.com")
users.first(active=True)
users.all(limit=100)
```

Advanced users can escape to backend-native queries:

```python
users.backend
users.table
users.engine
```

ModelVault should not become a full ORM query language.

---

# Bulk Operations

```python
users.insert_many(records)
users.upsert_many(records)

users.delete_many(keys)

users.validate_all()
```

Bulk methods return reports instead of raw counts.

---

# Validation

```python
report = users.validate_all()

report.valid_count
report.invalid_count
report.errors
```

Validation policies:

```python
Vault(
    "...",
    validation="strict",
)
```

Modes:

- strict
- warn
- report

---

# Health

```python
health = vault.health()

health.backend
health.schemas
health.validation
health.drift
health.indexes
```

---

# Inspection

```python
vault.models()

vault.describe(User)

vault.status(User)
```

Example:

```text
Collection: User
Backend: SQLite
Storage: Hybrid
Schema: Current
Records: 12,411
```

---

# Storage Modes

```python
StorageMode.TABLE
StorageMode.DOCUMENT
StorageMode.HYBRID
```

---

# Reports

Every operation that performs analysis returns a typed report.

```python
HealthReport
ValidationReport
DriftReport
MigrationPlan
CollectionStatus
```

---

# Exceptions

```python
ModelVaultError

BackendError
ValidationError
MigrationError
DriftDetectedError
RecordNotFoundError
```

---

# Hooks (Future)

```python
@before_insert
@after_insert

@before_update
@after_update

@after_load

@before_delete
```

---

# Async API (Future)

```python
vault = AsyncVault(...)

users = vault.collection(User)

await users.insert(user)
await users.get(1)
```

Method names remain identical.

---

# SQLAlchemy Escape Hatch

ModelVault is not intended to replace SQLAlchemy.

Developers should always have access to the underlying objects.

```python
users.engine
users.metadata
users.table
users.backend
```

This allows advanced SQLAlchemy workflows without abandoning ModelVault.

---

# Data Import / Export

```python
users.export_json(...)
users.export_csv(...)
users.export_parquet(...)

users.import_json(...)
users.import_dataframe(df)
```

---

# Example

```python
from pydantic import BaseModel, EmailStr
from modelvault import Vault, model


@model(
    key="id",
    storage="hybrid",
    indexes=["email"],
)
class User(BaseModel):
    id: int
    email: EmailStr
    active: bool = True


vault = Vault.sqlite("app.db")

users = vault.collection(User)

users.insert(User(id=1, email="alice@example.com"))

user = users.get(1)

print(user.email)

print(vault.health())
```

---

# API Philosophy

The public API should feel like working with domain models, not database tables.

Developers should think:

```python
users.insert(user)
```

instead of:

```python
session.execute(...)
```

while still retaining an escape hatch into SQLAlchemy when needed.

The API should remain intentionally small. Every new public method should strengthen ModelVault's core promise:

> Keep application models valid, versioned, and trustworthy while relying on databases users already trust.
