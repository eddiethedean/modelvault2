# CONTRACTS.md

# Persistence Contracts

> **A Persistence Contract is the central abstraction of ModelVault.**

ModelVault is not built around tables, ORM classes, or database sessions. It is built around **contracts**.

A Persistence Contract describes how a Pydantic model should live over time: how it is identified, validated, serialized, stored, indexed, versioned, migrated, inspected, and trusted.

The contract is the bridge between an application model and a trusted database.

---

# Why Contracts Exist

Pydantic models are excellent at describing valid Python data.

Databases are excellent at durable storage.

But the relationship between the two is usually handwritten, scattered, and fragile.

Typical application code spreads persistence rules across:

- Pydantic models
- SQLAlchemy models
- Alembic migrations
- repository classes
- service functions
- custom serializers
- database indexes
- operational scripts
- documentation

ModelVault consolidates those rules into one explicit artifact:

> **The Persistence Contract.**

The contract does not replace the model. It describes how the model is persisted.

---

# The Contract in One Sentence

A Persistence Contract is a versioned, inspectable, backend-aware declaration of how a Pydantic model is validated, serialized, stored, queried, migrated, and checked for integrity.

---

# Example

```python
from uuid import UUID
from pydantic import BaseModel, EmailStr
from modelvault import model


@model(
    key="id",
    storage="hybrid",
    indexes=["email", "active"],
)
class User(BaseModel):
    id: UUID
    email: EmailStr
    active: bool = True
```

This creates a Persistence Contract for `User`.

Conceptually:

```python
PersistenceContract(
    model=User,
    model_name="User",
    python_path="app.models.User",
    key_field="id",
    storage_mode="hybrid",
    indexes=["email", "active"],
    schema_hash="...",
    serializer="default",
    validation_policy="strict",
)
```

From this, ModelVault can produce:

- SQL schema
- metadata records
- indexes
- typed collection behavior
- serialization rules
- validation rules
- drift reports
- migration plans
- health checks

---

# Contract Responsibilities

A Persistence Contract answers the following questions.

## Identity

What model does this contract describe?

```text
model_name
python_path
collection_name
table_name
```

## Key

How are records uniquely identified?

```text
key_field
key_type
key_serializer
```

## Shape

What is the model schema?

```text
pydantic_schema
field_definitions
required_fields
optional_fields
defaults
nested_models
```

## Storage

How should records be represented in the database?

```text
storage_mode
table_name
column_fields
json_payload_field
document_table
```

## Indexing

Which fields should be queryable?

```text
indexes
unique_indexes
compound_indexes
```

## Serialization

How are Python values converted to database-safe values?

```text
serializer
field_serializers
json_encoder
backend_type_mapping
```

## Validation

When and how should validation occur?

```text
write_validation
read_validation
bulk_validation
migration_validation
```

## Versioning

How does ModelVault know if the model changed?

```text
schema_hash
contract_hash
contract_version
created_at
supersedes
```

## Migration

How can stored data move from one contract to another?

```text
from_hash
to_hash
change_set
migration_plan
safety_level
```

## Health

How can ModelVault determine whether this contract is healthy?

```text
schema_current
indexes_present
records_valid
metadata_valid
drift_status
```

---

# Contract Lifecycle

```text
Pydantic Model
      ↓
Contract Declaration
      ↓
Contract Builder
      ↓
Persistence Contract
      ↓
Fingerprint
      ↓
Registry
      ↓
Execution Plan
      ↓
Backend Operations
      ↓
Database
```

## 1. Declaration

The user declares persistence behavior.

```python
@model(key="id", storage="table")
class User(BaseModel):
    ...
```

## 2. Building

ModelVault inspects:

- Pydantic model schema
- decorator options
- defaults
- field metadata
- backend requirements

and creates a normalized contract.

## 3. Fingerprinting

ModelVault generates a deterministic hash from the contract.

This hash changes when meaningful persistence behavior changes.

## 4. Registration

The contract is stored in ModelVault metadata tables inside the database.

## 5. Planning

For each operation, ModelVault creates an execution plan from the contract.

## 6. Execution

The backend executes the plan against SQLite, PostgreSQL, DuckDB, or another trusted database.

## 7. Inspection

The contract can later be used for health checks, validation reports, migration planning, and drift detection.

---

# Contract vs Model

The Pydantic model describes valid data.

The Persistence Contract describes durable model behavior.

```text
Pydantic Model
  - fields
  - validation
  - types
  - defaults
  - domain shape

Persistence Contract
  - key
  - storage mode
  - indexes
  - serializer
  - schema hash
  - migration behavior
  - backend expectations
```

ModelVault should avoid forcing users to subclass a custom base class.

Persistence should be opt-in and attachable.

Preferred:

```python
@model(key="id", storage="hybrid")
class User(BaseModel):
    ...
```

Also supported:

```python
vault.register(User, key="id", storage="hybrid")
```

---

# Contract vs Collection

A Collection is the runtime interface for working with records.

A Contract is the durable definition of how those records should behave.

```text
Persistence Contract
      ↓
Collection[User]
      ↓
insert/get/find/delete
```

Collections are generated from or backed by contracts.

The contract is more fundamental.

---

# Contract vs Database Schema

A database schema is a physical implementation detail.

A contract is a model-level source of truth.

For example, this contract:

```python
@model(key="id", storage="hybrid", indexes=["email"])
class User(BaseModel):
    id: UUID
    email: EmailStr
    profile: Profile
```

might compile to:

```text
users
  id TEXT PRIMARY KEY
  email TEXT
  __modelvault_data JSON
  __schema_hash TEXT
```

The database schema is only one artifact produced from the contract.

---

# Contract vs Migration

A migration transforms persisted data from one contract version to another.

```text
Contract v1
      ↓
Migration Plan
      ↓
Contract v2
```

Migrations do not define the truth.

They reconcile stored data with the new contract.

---

# Contract Structure

A future internal contract object may look like this:

```python
@dataclass(frozen=True)
class PersistenceContract:
    model_type: type[BaseModel]
    model_name: str
    python_path: str

    collection_name: str
    table_name: str | None

    key: KeyDefinition
    storage: StorageDefinition
    indexes: tuple[IndexDefinition, ...]

    schema: ModelSchema
    serializer: SerializerDefinition
    validation: ValidationDefinition

    version: ContractVersion
    metadata: ContractMetadata
```

Supporting objects:

```python
@dataclass(frozen=True)
class KeyDefinition:
    field: str
    type_name: str
    required: bool
    serializer: str | None = None
```

```python
@dataclass(frozen=True)
class StorageDefinition:
    mode: Literal["table", "document", "hybrid"]
    table_name: str
    column_fields: tuple[str, ...]
    document_field: str | None
```

```python
@dataclass(frozen=True)
class IndexDefinition:
    fields: tuple[str, ...]
    unique: bool = False
    name: str | None = None
```

```python
@dataclass(frozen=True)
class ValidationDefinition:
    on_write: Literal["strict", "warn", "disabled"]
    on_read: Literal["strict", "warn", "disabled"]
    on_bulk: Literal["strict", "report"]
```

---

# Fingerprinting

A contract fingerprint is a deterministic hash that identifies the effective persistence behavior of a contract.

It should include:

- model field names
- field types
- required/optional status
- defaults that affect persistence
- key field
- storage mode
- indexed fields
- serialization settings
- validation policy
- relevant ModelVault contract version

It should not include:

- comments
- docstring changes unless configured
- formatting
- Python object memory addresses
- non-persistence runtime state

## Example

```text
User Contract v1
  id: UUID
  email: EmailStr
  storage: hybrid
  key: id
  indexes: email

hash: 1b814a...
```

Add a field:

```python
phone: str | None = None
```

New hash:

```text
hash: 8e92ff...
```

ModelVault can now detect drift.

---

# Contract Change Classification

When a contract changes, ModelVault should classify the change.

## Safe Changes

Usually safe:

- add nullable field
- add field with default
- add non-unique index
- add metadata-only description
- widen compatible type

## Review Required

Needs developer review:

- rename field
- change serializer
- change storage mode
- add unique index
- change nested model structure
- change validation policy

## Unsafe Changes

Usually unsafe:

- remove required field
- change key field
- narrow type
- remove indexed field used by queries
- change collection/table identity
- make nullable field required without default

---

# Contract Registry

Contracts are persisted in registry tables.

Minimum registry data:

```text
collection_name
model_name
python_path
contract_hash
schema_json
storage_mode
key_field
table_name
created_at
updated_at
```

The registry allows ModelVault to answer:

- What models exist?
- What contract version is current?
- What schemas have existed before?
- Are migrations pending?
- Does the runtime model match the database metadata?
- Is the database healthy?

---

# Execution Plans

A contract is static.

An execution plan is operation-specific.

```text
Persistence Contract
      ↓
Execution Planner
      ↓
InsertPlan / ReadPlan / MigrationPlan / ValidationPlan
      ↓
Backend
```

Examples:

```text
InsertPlan
  validate User
  serialize User
  extract indexed fields
  write hybrid row
  record validation event if failure
```

```text
ReadPlan
  fetch row by key
  reconstruct payload
  validate User
  return User
```

```text
MigrationPlan
  compare old/new contract
  classify changes
  produce SQL and validation steps
```

Execution plans let ModelVault remain declarative without pretending every backend behaves the same.

---

# Contract Compilation

ModelVault may be described as a contract compiler.

The input is a Pydantic model plus persistence metadata.

The output is backend-specific behavior.

```text
Input:
  User model
  key="id"
  storage="hybrid"
  indexes=["email"]

Compiler Output:
  CREATE TABLE users (...)
  CREATE INDEX ...
  metadata rows
  Collection[User]
  validation rules
  migration diff rules
```

The compiler is not necessarily a separate command. It may run at registration time, startup time, migration planning time, or operation time.

---

# Storage Modes in Contracts

Contracts specify storage mode.

## Table Contract

```python
@model(key="id", storage="table")
class User(BaseModel):
    ...
```

The contract compiles to one table with model fields as columns.

## Document Contract

```python
@model(key="id", storage="document")
class AuditEvent(BaseModel):
    ...
```

The contract compiles to document storage with JSON payloads.

## Hybrid Contract

```python
@model(
    key="id",
    storage="hybrid",
    indexes=["email", "active"],
)
class User(BaseModel):
    ...
```

The contract compiles to indexed columns plus a complete JSON representation.

Hybrid is the preferred default for many application models because it balances queryability and model round-tripping.

---

# Backend Requirements

Contracts may require backend capabilities.

Examples:

```text
requires_json
requires_transactions
requires_unique_index
requires_generated_columns
requires_full_text_search
```

If a backend cannot satisfy the contract, registration should fail clearly.

Example:

```text
ContractError:
  User requires JSONB indexing, but the selected backend is SQLite.
```

ModelVault should not silently degrade contract guarantees.

---

# Contract Declaration API

Primary declaration style:

```python
@model(
    key="id",
    storage="hybrid",
    indexes=["email"],
)
class User(BaseModel):
    id: int
    email: EmailStr
```

Manual registration:

```python
vault.register(
    User,
    key="id",
    storage="hybrid",
    indexes=["email"],
)
```

Possible future explicit contract object:

```python
UserContract = Contract(
    model=User,
    key="id",
    storage=Hybrid(indexes=["email"]),
)
```

This may be useful when one model needs multiple persistence contracts.

---

# Multiple Contracts Per Model

A single Pydantic model may eventually support multiple contracts.

Example:

```python
OperationalUser = Contract(
    model=User,
    name="users",
    storage=Hybrid(indexes=["email"]),
)

AnalyticsUser = Contract(
    model=User,
    name="users_analytics",
    storage=Table(),
)
```

This allows one domain model to be stored differently for different workloads.

This should not be part of v0.1, but the architecture should not prevent it.

---

# Contract Invariants

Every contract must guarantee:

1. It references a valid Pydantic model.
2. It has a deterministic identity.
3. It has a key field.
4. Its key field exists on the model.
5. Its storage mode is supported by the backend.
6. Its fingerprint is deterministic.
7. It can be serialized to metadata.
8. It can be compared to prior versions.
9. It can produce execution plans.
10. It can validate data on read and write.

---

# Contract Health

A contract is healthy when:

- the runtime model imports successfully
- the stored contract hash matches the runtime contract hash
- required metadata exists
- required tables exist
- required indexes exist
- recent validation checks pass
- no unresolved unsafe migration exists
- backend capabilities satisfy requirements

A contract is unhealthy when any of these fail.

---

# Contract Inspection

Example API:

```python
vault.describe(User)
```

Possible output:

```text
User

Contract
  hash: 8e92ff...
  key: id
  storage: hybrid
  table: users

Model
  python path: app.models.User
  fields: id, email, active, profile

Indexes
  email
  active

Status
  schema: current
  validation: healthy
  drift: none
```

---

# Contract-Driven Development Workflow

A typical workflow:

1. Define a Pydantic model.
2. Add a ModelVault contract.
3. Run `modelvault check`.
4. ModelVault creates metadata and storage artifacts.
5. Application reads/writes through collections.
6. Model changes.
7. ModelVault detects contract drift.
8. Developer reviews migration plan.
9. Registry updates after migration.

This turns persistence into an inspectable lifecycle instead of scattered application code.

---

# v0.1 Contract Scope

The first implementation should support a narrow but complete contract system.

## Required

- Pydantic v2 models
- decorator declaration
- manual registration
- key field
- storage mode
- table name
- indexes
- schema fingerprint
- persisted registry metadata
- SQLite backend compatibility
- table storage
- read/write validation

## Deferred

- multiple contracts per model
- custom serializers
- custom validation policies
- advanced index definitions
- compound indexes
- backend capability negotiation
- contract inheritance
- contract plugins
- encryption requirements
- full migration application

---

# Design Risks

## Risk: Contracts Become Too Large

Mitigation:

- keep v0.1 contracts minimal
- separate required fields from optional policies
- store extensible metadata as JSON

## Risk: Contracts Hide Database Reality

Mitigation:

- expose generated schema
- expose SQLAlchemy escape hatches
- document backend differences clearly

## Risk: Fingerprints Change Too Often

Mitigation:

- define stable fingerprint inputs
- exclude irrelevant runtime details
- version the fingerprint algorithm

## Risk: Contracts Become an ORM

Mitigation:

- keep query API small
- avoid mapper/session abstractions
- focus on integrity, not object graph management

---

# North Star

Every contract feature should strengthen this promise:

> **A developer can look at a Pydantic model and its Persistence Contract and understand exactly how that model is stored, validated, versioned, migrated, and trusted.**

If a feature does not make the model lifecycle more understandable or trustworthy, it probably does not belong in the contract layer.
