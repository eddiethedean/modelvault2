# COMPONENT_MODEL.md

# Component Model

This document defines the runtime component model for ModelVault.

## Chapter 1 — System Overview

ModelVault is organized as a layered, contract-driven architecture.

```
Application
    ↓
Vault
    ↓
Persistence Contract
    ↓
Execution Planner
    ↓
Execution Plans
    ↓
Storage Strategy
    ↓
Backend
    ↓
Trusted Database
```

### Architectural Goals

- Separate model semantics from persistence.
- Keep components cohesive and loosely coupled.
- Make every operation inspectable.
- Favor composition over inheritance.

## Chapter 2 — Core Runtime Components

### Vault

Coordinates the entire runtime.

Responsibilities:

- Backend lifecycle
- Registry access
- Collection creation
- Health checks
- Migration orchestration

### PersistenceContract

Immutable description of how a Pydantic model is persisted.

Owns:

- Key definition
- Storage mode
- Schema fingerprint
- Validation policy
- Index definitions

### ContractRegistry

Persistent catalog of contracts.

Tracks:

- Registered contracts
- Historical versions
- Metadata
- Migration history

### Collection

Public façade for CRUD operations.

Collections delegate work to the Execution Planner and never talk directly to SQL.

## Chapter 3 — Planning Components

### ExecutionPlanner

Transforms a PersistenceContract plus an operation into an executable plan.

Plan types:

- InsertPlan
- ReadPlan
- UpdatePlan
- DeletePlan
- ValidationPlan
- DiffPlan
- MigrationPlan
- ExportPlan

Plans are immutable.

## Chapter 4 — Infrastructure Components

### StorageStrategy

Responsible for mapping contracts to physical storage.

Implementations:

- TableStorage
- HybridStorage
- DocumentStorage

### Backend

Responsible for database execution.

Implementations:

- SQLAlchemyBackend
- SQLiteBackend
- PostgreSQLBackend
- DuckDBBackend

### Serializer

Converts models into backend-safe payloads and reconstructs them on reads.

### Validator

Applies contract validation on writes, reads, bulk scans, and migrations.

## Chapter 5 — Operational Components

Operational services include:

- HealthManager
- MigrationManager
- CapabilityValidator
- ReportGenerator
- PluginManager

These services coordinate diagnostics rather than persistence.

## Chapter 6 — Component Relationships

Typical insert flow:

```
Collection
    ↓
ExecutionPlanner
    ↓
InsertPlan
    ↓
StorageStrategy
    ↓
Backend
    ↓
Database
```

Typical read flow:

```
Collection
    ↓
ExecutionPlanner
    ↓
ReadPlan
    ↓
Backend
    ↓
Validator
    ↓
Model
```

## Chapter 7 — Component Rules

Architectural invariants:

- Contracts are immutable.
- Collections never generate SQL.
- Backends never inspect Pydantic models.
- Storage strategies never own metadata.
- Registry never performs CRUD.
- Planner produces plans but never executes them.
- Validation is a separate concern from storage.

## Chapter 8 — Reference Component Template

Every component should document:

- Purpose
- Responsibilities
- Owns
- Depends On
- Creates
- Used By
- Thread Safety
- Extension Points
- Public Interface
- Internal Interface
- Lifecycle

## v0.17 Component Set

Required:

- Vault
- PersistenceContract
- ContractRegistry
- Collection
- ExecutionPlanner
- InsertPlan
- ReadPlan
- TableStorage
- SQLAlchemyBackend
- SQLiteBackend
- Serializer
- Validator

## North Star

ModelVault is a contract-driven execution engine for model integrity.

Every component exists to preserve the trustworthiness of application models while delegating storage to proven database technology.
