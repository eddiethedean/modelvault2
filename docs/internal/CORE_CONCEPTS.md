# CORE_CONCEPTS.md

# Core Concepts

This document defines the fundamental vocabulary of ModelVault.

Every API, backend, plugin, and feature should be expressible using these concepts. If a new feature cannot be explained in terms of them, either the feature or the concepts should be reconsidered.

## Philosophy

ModelVault is **model-centric**, not table-centric.

Traditional persistence stacks look like:

```
Database
    ↓
Tables
    ↓
ORM
    ↓
Application Models
```

ModelVault inverts that relationship:

```
Application Models
        ↓
Persistence Contracts
        ↓
Collections
        ↓
Backends
        ↓
Trusted Databases
```

The model is the source of truth.

---

# The Core Primitives

ModelVault intentionally has a very small set of primary abstractions.

1. Model
2. Persistence Contract
3. Collection
4. Vault
5. Registry
6. Backend
7. Storage Strategy

Everything else is derived from these.

---

# 1. Model

A Model is an ordinary Pydantic model describing business data.

```python
class User(BaseModel):
    id: UUID
    email: EmailStr
```

ModelVault never replaces Pydantic. Models remain plain Pydantic types that can be used without ModelVault.

**Responsibilities**

- validation rules
- business semantics
- serialization shape
- documentation

A model does **not** know how it is stored.

---

# 2. Persistence Contract

A Persistence Contract describes how a model is persisted.

```python
@model(
    key="id",
    storage="hybrid",
    indexes=["email"],
)
class User(BaseModel):
    ...
```

It answers questions such as:

- What is the primary key?
- Which backend capabilities are required?
- Which storage strategy should be used?
- Which fields are indexed?
- How is the model versioned?

This separation keeps domain logic independent from persistence.

---

# 3. Collection

A Collection is the persistence interface for one model type.

```
Collection[User]
```

Collections expose typed CRUD, validation, import/export, and querying.

Collections return model instances—not rows.

They are conceptually closer to a repository than an ORM session.

---

# 4. Vault

A Vault represents one logical persistence environment.

```
vault = Vault("sqlite:///app.db")
```

The Vault owns:

- backend lifecycle
- collection creation
- registry access
- metadata
- migrations
- health checks

The Vault does **not** own the data itself. The underlying database does.

---

# 5. Registry

The Registry is the catalog of every persistence contract known to a Vault.

It records:

- registered models
- schema fingerprints
- storage strategies
- migrations
- backend metadata

The Registry is persisted in metadata tables inside the database.

It allows ModelVault to explain **what** exists before interacting with any records.

---

# 6. Backend

A Backend adapts ModelVault concepts to a storage engine.

Examples:

- SQLite
- PostgreSQL
- DuckDB

Backends are responsible for:

- connections
- transactions
- SQL generation
- reading and writing records

Backends are **not** responsible for validation or model semantics.

---

# 7. Storage Strategy

A Storage Strategy determines how a model is represented inside a backend.

Planned strategies:

- Table
- Document
- Hybrid

Applications may use different strategies for different models while sharing the same API.

---

# Derived Concepts

These concepts are built from the primitives.

## Schema Fingerprint

A deterministic hash representing the persistence contract.

## Drift

A mismatch between the stored contract and the current contract.

## Migration

A transformation that reconciles contract versions.

## Validation Report

A structured assessment of record integrity across a collection.

## Health Report

A system-wide assessment of registry, backend, schema, and validation state.

---

# Lifecycle

```
Pydantic Model
        ↓
Persistence Contract
        ↓
Registry
        ↓
Collection
        ↓
Backend
        ↓
Database

Database
        ↓
Backend
        ↓
Collection
        ↓
Validation
        ↓
Model
```

Every interaction with persistent data flows through this lifecycle.

---

# Invariants

Every implementation of ModelVault must guarantee:

1. Models remain ordinary Pydantic models.
2. Data is stored in trusted databases.
3. Reads return validated models.
4. Writes validate before persistence.
5. Metadata remains inspectable.
6. Contracts are versioned.
7. Drift is detectable.
8. Users retain full ownership of their data.
9. No proprietary storage format is required.
10. ModelVault may disappear without making user data inaccessible.

---

# Mental Model

Think of the primitives like this:

- **Model** — What the application knows.
- **Persistence Contract** — How the model should live.
- **Collection** — Where the model is manipulated.
- **Vault** — The coordinator.
- **Registry** — The catalog.
- **Backend** — The translator.
- **Database** — The durable storage.

Everything else in ModelVault exists to strengthen the integrity of that flow.
