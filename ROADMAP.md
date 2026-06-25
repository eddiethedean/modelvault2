# ModelVault Roadmap

This document defines the versioned delivery plan for ModelVault from **v0.17** (first public release) through a stable **v1.0**.

Each phase has a clear theme, explicit scope boundaries, and measurable success criteria. Later phases build on earlier ones; features marked **deferred** are intentionally out of scope until their target version.

---

## Guiding Principle

> **Your models are your source of truth. ModelVault keeps them that way.**

Every release should make Pydantic models more trustworthy across the persistence lifecycle while keeping storage grounded in databases developers already trust.

---

## Version Overview

| Version | Theme | Primary outcome |
|---------|-------|-----------------|
| **v0.17** | Prove the architecture | Pydantic models persist to SQLite with validation and registry metadata |
| **v0.18** | Expand storage and observability | Multiple storage strategies, structured health and validation reports |
| **v0.19** | Model lifecycle intelligence | Drift classification, migration planning, operational CLI |
| **v0.20** | Production backends and async | PostgreSQL, async collections, Alembic integration |
| **v0.21** | Analytics and data interchange | DuckDB, DataFrame and Parquet interoperability |
| **v1.0** | Stability and guarantees | Frozen public API, long-term compatibility commitments |

### Versioning policy

ModelVault uses **semantic versioning**. Pre-1.0 releases increment the minor version for each planned milestone:

```text
v0.17 → v0.18 → v0.19 → v0.20 → v0.21 → v1.0
```

- **v0.17** is the first implementable release (architecture proof on SQLite).
- **v0.18–v0.21** each add a major capability layer without breaking the prior release's contracts.
- **v0.22–v0.99** are reserved for patch releases, release candidates, and unplanned course corrections before 1.0.
- **v1.0** freezes the public API and begins long-term compatibility guarantees.

---

## v0.17 — Architecture Proof

**Theme:** Prove that a Pydantic model can become a persistence contract, be registered in database metadata, execute through a planner, persist in SQLite, and load back as a validated model.

**Product statement:** ModelVault v0.17 is a SQLite-backed model integrity layer for ordinary Pydantic v2 models.

### In scope

#### Public API

- `Vault(url)` and `Vault.sqlite(path)`
- `@model(key, storage="table", indexes, table_name)`
- `vault.register()`, `vault.collection()`, `vault.models()`, `vault.describe()`, `vault.health()`, `vault.close()`
- `Collection[T]` with: `insert`, `upsert`, `get`, `delete`, `exists`, `count`, `all`, `find`, `validate_all`

#### Core internals

- Error hierarchy (`ModelVaultError` and typed subclasses)
- `PersistenceContract` builder from decorated Pydantic models
- Deterministic contract fingerprints (algorithm-versioned)
- Execution planner (`InsertPlan`, `ReadPlan`, `UpsertPlan`, `DeletePlan`, `CountPlan`, `FindPlan`, `ValidateAllPlan`)
- Write validation and read validation (strict by default)
- Serialization round-trip for common field types

#### Storage

- **Table storage only** — one SQL table per model
- Simple scalar columns; nested/complex fields stored as JSON text
- Single-column primary keys
- Simple single-field non-unique indexes

#### Backend

- **SQLite** via **SQLAlchemy Core** (not ORM)
- Connection lifecycle, transactions, DDL, CRUD execution

#### Registry

Metadata tables:

- `modelvault_registry`
- `modelvault_schemas`
- `modelvault_validation_events`

#### Integrity

- Basic drift detection (current contract vs stored contract; report only, no auto-migration)
- Basic `vault.health()` (connectivity, metadata presence, schema status)

#### Supported field types

`str`, `int`, `float`, `bool`, `datetime`, `date`, `UUID`, `Decimal`, `Enum`, `Optional`, `list`/`dict` (JSON), nested `BaseModel` (JSON)

### Out of scope

- PostgreSQL, DuckDB, async API
- Document and hybrid storage
- Alembic integration and automatic migrations
- Plugin system, encryption, caching, multi-tenancy
- Relationships, foreign keys, joins, query DSL
- Full CLI
- Pandas, Polars, PyArrow integrations
- Schema-altering migrations beyond initial table creation

### Success criteria

v0.17 is complete when a developer can:

1. Define a Pydantic model and register it with `@model`.
2. Open a SQLite vault and obtain a typed collection.
3. Insert, read, upsert, delete, count, and find records with validation on every read and write.
4. Inspect registry metadata and deterministic contract hashes in the database.
5. Detect drift when the model contract changes (without automatic repair).
6. Run a test suite covering the full persistence path.

### Example target

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

---

## v0.18 — Storage Strategies and Observability

**Theme:** Support real-world model shapes and give operators clear visibility into collection health.

**Depends on:** v0.17 contract layer, registry, and collection API.

### In scope

#### Storage strategies

- **Document storage** — full model serialized as JSON; ideal for nested, flexible, or audit-style records
- **Hybrid storage** — indexed SQL columns plus complete validated JSON payload; recommended default for most apps
- Per-model `storage` selection via `@model(storage="table" | "document" | "hybrid")`
- Strategy-specific schema compilation and queryable field extraction (hybrid)

#### Reports

- Structured `ValidationReport` from `validate_all()` and bulk operations
- Structured `HealthReport` from `vault.health()` covering:
  - backend connectivity
  - metadata integrity
  - schema and index status
  - validation sampling (optional scan)

#### Collection enhancements

- Improved `find()` for hybrid/document indexed fields
- Bulk insert/update helpers with aggregated error collection
- `CollectionDescription` via `vault.describe(model)`

#### Registry

- `modelvault_migrations` metadata table (history records; planning still deferred to v0.19)
- `modelvault_indexes` metadata table

### Out of scope

- PostgreSQL-specific features (JSONB optimizations)
- Automatic migration application
- Async collections
- Alembic code generation
- Plugin hooks
- Full operational CLI

### Success criteria

v0.18 is complete when a developer can:

1. Choose table, document, or hybrid storage per model on the same vault.
2. Round-trip nested models reliably under document and hybrid modes.
3. Query indexed fields in hybrid collections with `find()`.
4. Run `validate_all()` and receive a structured report of failures.
5. Run `vault.health()` and receive an actionable health summary.

---

## v0.19 — Drift, Migrations, and CLI

**Theme:** Turn contract changes into understandable lifecycle events with safe operational tooling.

**Depends on:** v0.18 storage strategies and report infrastructure.

### In scope

#### Schema intelligence

- Rich **schema fingerprints** with explicit algorithm versioning and changelog in metadata
- **Drift detection** with classified outcomes:
  - compatible (no action)
  - safe migration
  - review required
  - unsafe / incompatible
- `DriftReport` and `vault.describe(model)` drift sections

#### Migration planning

- **Migration plans** generated from contract diffs (plans only — no automatic application of unsafe changes)
- Migration change categories: safe, review required, unsafe
- Registry migration history in `modelvault_migrations`
- `MigrationPlan` type exposed in public API

#### CLI (initial release)

```bash
modelvault check      # vault health
modelvault inspect    # registry and collection metadata
modelvault diff       # contract vs stored fingerprint
modelvault validate   # collection validation scan
modelvault plan-migration
```

#### Validation policy modes

- `strict` (default) — raise on validation error
- `warn` — log and return when possible
- `report` — collect into `ValidationReport`
- `disabled` — internal/testing only

### Out of scope

- Alembic revision file generation (v0.20)
- PostgreSQL and DuckDB backends
- Async API
- Automatic unsafe migrations
- Plugin system

### Success criteria

v0.19 is complete when a developer can:

1. Change a model contract and receive a classified drift report.
2. Generate a migration plan describing required schema changes.
3. Inspect migration history in registry metadata.
4. Operate a vault from the CLI for check, inspect, diff, validate, and plan-migration workflows.
5. Configure validation policy per vault or collection where appropriate.

---

## v0.20 — Production Backends and Async

**Theme:** Run ModelVault in production on PostgreSQL with async frameworks and Alembic-aware workflows.

**Depends on:** v0.19 migration planning and stable storage strategies.

### In scope

#### Backends

- **PostgreSQL** via SQLAlchemy Core
- JSONB support for document and hybrid storage
- Backend capability matrix documented (what each backend supports)
- Minimal code changes when switching SQLite ↔ PostgreSQL (connection URL and backend-specific options only)

#### Async API

- `AsyncVault`, `AsyncCollection[T]`
- Async equivalents of core CRUD and validation operations
- Compatible with FastAPI and other async Python stacks

#### Alembic integration

- Generate Alembic revision suggestions from `MigrationPlan`
- `modelvault alembic revision` CLI command
- Documented workflow: ModelVault plans → Alembic applies → registry updated

#### Production hardening

- Connection pooling configuration
- Improved transaction boundaries and error recovery
- Index management for PostgreSQL (including JSONB path indexes where applicable)

### Out of scope

- DuckDB backend
- DataFrame and Parquet export/import
- Plugin system
- Distributed or multi-region concerns

### Success criteria

v0.20 is complete when a developer can:

1. Deploy the same model contracts against PostgreSQL in production.
2. Use async collections in an async web service.
3. Export a migration plan to an Alembic revision workflow.
4. Switch between SQLite (dev) and PostgreSQL (prod) with connection-string-level changes only.

---

## v0.21 — Analytics and Data Interchange

**Theme:** Treat model collections as analytical datasets and interoperate with the Python data stack.

**Depends on:** v0.20 backend abstraction and stable serialization.

### In scope

#### Backend

- **DuckDB** backend (SQLAlchemy dialect and/or native adapter as reliability dictates)
- Analytical query patterns over collections

#### Data interchange

- Export collections to **Pandas**, **Polars**, and **PyArrow** tables
- **Parquet** import and export
- Notebook-friendly APIs for local analytics and experiment tracking

#### Use cases enabled

- Model collections as queryable datasets
- Offline analysis without leaving validated model boundaries
- Parquet-based archival and sharing

### Out of scope

- Real-time streaming pipelines
- Full SQL analytics query builder (escape hatches to backend-native SQL remain the advanced path)
- v1.0 API freeze work

### Success criteria

v0.21 is complete when a developer can:

1. Open a DuckDB-backed vault for analytical workloads.
2. Export a collection to a DataFrame and round-trip selected records.
3. Read and write Parquet files through ModelVault collection APIs.
4. Use the same model contracts across SQLite, PostgreSQL, and DuckDB.

---

## v1.0 — Stable Public API

**Theme:** Long-term stability, documentation completeness, and compatibility guarantees.

**Depends on:** All v0.x phases delivering their stated success criteria.

### In scope

#### API stability

- Frozen public surface: `Vault`, `Collection`, `@model`, core report types, and documented extension points
- Semantic versioning policy for post-1.0 releases
- Deprecation policy with minimum notice periods

#### Documentation

- Complete API reference
- Backend compatibility matrix
- Storage strategy selection guide
- Migration and operations runbooks
- Production deployment examples (SQLite dev, PostgreSQL prod, DuckDB analytics)

#### Quality bar

- High test coverage across backends and storage strategies
- Performance benchmarks for common CRUD paths
- Documented validation policy tradeoffs

#### Compatibility guarantees

- Ordinary Pydantic models remain the integration point
- Data remains accessible in standard database tools without ModelVault
- Breaking changes only in major versions after 1.0

### Success criteria

v1.0 is complete when a developer can:

1. Define a Pydantic model, register it, persist and retrieve validated records.
2. Detect schema drift and generate migration plans.
3. Move between SQLite, PostgreSQL, and DuckDB with minimal code changes.
4. Inspect all model metadata directly from database tables.
5. Rely on documented API stability for production adoption.

This matches the mission defined in the technical specification: model-centric persistence that is simple, trustworthy, and portable.

---

## Cross-Version Principles

These constraints apply to every release:

| Principle | Requirement |
|-----------|-------------|
| Models first | Domain models drive persistence, not tables |
| Trust existing databases | No custom storage engine; SQLite, PostgreSQL, DuckDB own durability |
| Validate the lifecycle | Writes and reads validate by default |
| Zero lock-in | Data lives in normal SQL tables inspectable without ModelVault |
| Small public API | Repository-oriented collections, not ORM sessions |
| Boring underneath | SQLAlchemy Core for SQL; Alembic for applied migrations (v0.20+) |

---

## Deferred Beyond v1.0

The following are anticipated but not scheduled for any v0.x release:

- Plugin system (auditing, encryption, soft delete, multi-tenancy, event publishing)
- Relationship and foreign-key modeling
- Full query DSL
- Automatic application of unsafe migrations
- Caching layer
- Multi-contract registration per model type

These may be revisited based on adoption feedback after 1.0.

---

## Current Status

**ModelVault is in the design phase.** No implementation code exists yet.

The immediate next step is **v0.17 Phase 0**: scaffold `pyproject.toml`, `src/modelvault/`, and `tests/`, then follow the build order in [`docs/internal/IMPLEMENTATION_PLAN.md`](docs/internal/IMPLEMENTATION_PLAN.md).

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [`README.md`](README.md) | Project overview and quick example |
| [`docs/internal/MVP_SPEC.md`](docs/internal/MVP_SPEC.md) | Exact v0.17 scope |
| [`docs/internal/IMPLEMENTATION_PLAN.md`](docs/internal/IMPLEMENTATION_PLAN.md) | v0.17 build order |
| [`docs/internal/ARCHITECTURE.md`](docs/internal/ARCHITECTURE.md) | System design |
| [`docs/internal/SPEC.md`](docs/internal/SPEC.md) | Functional requirements |
