
# ModelVault

> **Your models are your source of truth. ModelVault keeps them that way.**

ModelVault is a **Model Integrity Platform** for Python. It bridges the gap between **Pydantic** and trusted databases such as **SQLite**, **PostgreSQL**, and **DuckDB**.

Instead of inventing a new database or another ORM, ModelVault treats your **Pydantic models as persistence contracts**. From those contracts it manages validation, schema tracking, metadata, drift detection, migration planning, and typed repositories while delegating storage to databases you already trust.

---

# Why ModelVault?

Python has excellent building blocks:

- Pydantic validates models.
- SQLAlchemy talks to SQL databases.
- Alembic manages schema migrations.
- SQLite and PostgreSQL provide durable storage.
- DuckDB powers local analytics.

Yet every project still reinvents the same layer:

- Mapping models to persistence
- Validation after data is read
- Schema version tracking
- Metadata management
- Repository boilerplate
- Drift detection
- Migration planning
- Operational health checks

ModelVault fills that missing layer.

---

# The Core Idea

Traditional persistence starts with the database.

```text
Database
   ↓
Tables
   ↓
ORM
   ↓
Application Models
```

ModelVault starts with the application model.

```text
Pydantic Model
      ↓
Persistence Contract
      ↓
ModelVault
      ↓
SQLite / PostgreSQL / DuckDB
```

The **model** becomes the source of truth.

The **database** remains the source of storage.

---

# The Persistence Contract

Every registered model becomes a persistence contract.

```python
from pydantic import BaseModel, EmailStr
from modelvault import model

@model(
    key="id",
    storage="hybrid",
    indexes=["email"],
)
class User(BaseModel):
    id: int
    email: EmailStr
    active: bool = True
```

From that single declaration ModelVault can derive:

- storage schema
- repository API
- schema fingerprint
- metadata
- migration plans
- validation rules
- health checks

The persistence contract—not the table—is the heart of ModelVault.

---

# Example

```python
from modelvault import Vault

vault = Vault.sqlite("app.db")

users = vault.collection(User)

users.insert(
    User(id=1, email="alice@example.com")
)

user = users.get(1)

print(user.email)
```

Reads and writes are validated automatically.

---

# What Makes ModelVault Different?

| Tool | Primary Focus | ModelVault |
|------|---------------|------------|
| SQLAlchemy | SQL toolkit & ORM | Uses SQLAlchemy underneath but focuses on model integrity |
| SQLModel | ORM models | Keeps ordinary Pydantic models and adds persistence contracts |
| Alembic | Schema migrations | Adds model-aware drift detection and migration planning |
| Beanie / ODMantic | MongoDB ODMs | Targets trusted SQL and analytical databases |
| TinyDB | JSON database | Does not invent storage; builds on proven databases |

---

# Guiding Principles

## Models First

Domain models drive persistence—not database tables.

## Trust Existing Databases

ModelVault intentionally delegates transactions, locking, indexing, recovery, and durability to established databases.

## Validate the Entire Lifecycle

Validation occurs:

- before writes
- after reads
- during migrations
- during integrity scans

## Zero Lock-In

If ModelVault disappeared tomorrow, your data would still live in normal SQLite, PostgreSQL, or DuckDB tables.

## Small Public API

```python
vault = Vault(...)

users = vault.collection(User)

users.insert(...)
users.get(...)
users.find(...)
users.validate_all()

vault.health()
vault.describe(User)
```

The API is intentionally repository-oriented rather than ORM-oriented.

---

# Storage Strategies

Choose the best representation for each model.

### Table

One SQL table per model.

Best for relational data.

### Document

Entire model stored as JSON.

Best for flexible or nested records.

### Hybrid

Indexed SQL columns plus the complete validated model as JSON.

Recommended for most applications.

---

# Planned Features

- Typed repositories
- Validation on read and write
- Schema fingerprinting
- Drift detection
- Model registry
- Metadata tables
- Migration planning
- Health reports
- Validation reports
- SQLite, PostgreSQL, and DuckDB backends
- Pandas / Polars / PyArrow interoperability
- Alembic integration
- Async API

---

# Project Philosophy

ModelVault is intentionally **boring underneath** and **opinionated above**.

We are not trying to replace SQLAlchemy, Alembic, PostgreSQL, or SQLite.

Instead, ModelVault provides the missing layer that keeps application models valid, synchronized, versioned, and understandable throughout their lifecycle.

---

# Roadmap

Pre-1.0 releases run from **v0.17** through **v0.21**, then **v1.0**. See [`ROADMAP.md`](ROADMAP.md) for full scope and success criteria per version.

### v0.17

- SQLite backend
- SQLAlchemy Core
- Typed collections
- Metadata registry
- Table storage
- Read/write validation

### v0.18

- Hybrid storage
- Document storage
- Validation reports
- Health checks

### v0.19

- Schema fingerprints
- Drift detection
- Migration planning

### v0.20

- PostgreSQL
- Async API
- Alembic integration

### v0.21

- DuckDB
- DataFrame interoperability
- Parquet support

### v1.0

Stable public API with long-term compatibility guarantees.

---

# Contributing

ModelVault is currently in the design phase.

The project is being built around one central promise:

> **Your models are your source of truth. ModelVault keeps them that way.**
