# EXECUTION_PLANNER.md

# Execution Planner

> The Planner is the heart of the ModelVault runtime.

## Purpose

The Planner transforms an immutable Persistence Contract plus a requested operation into an immutable Execution Plan. It never executes database operations itself.

```
Persistence Contract
        │
        ▼
      Planner
        │
        ▼
 Execution Plan
        │
        ▼
 Storage Strategy
        │
        ▼
     Backend
        │
        ▼
     Database
```

## Responsibilities

The Planner SHALL:

- Accept a Persistence Contract.
- Accept an operation (insert, read, update, delete, validate, migrate, etc.).
- Validate backend capabilities.
- Produce an immutable execution plan.
- Remain deterministic and side-effect free.

The Planner SHALL NOT:

- Execute SQL.
- Open database connections.
- Perform transactions.
- Validate Pydantic models.
- Serialize model payloads.

## Planner API

```python
planner.plan_insert(contract, model)
planner.plan_read(contract, key)
planner.plan_update(contract, model)
planner.plan_delete(contract, key)
planner.plan_validate(contract)
planner.plan_diff(old_contract, new_contract)
planner.plan_migration(old_contract, new_contract)
```

## Planning Pipeline

```
Collection.insert()
        │
        ▼
Planner
        │
        ▼
Capability Validation
        │
        ▼
Execution Plan
        │
        ▼
Storage Strategy
        │
        ▼
Backend.execute(plan)
```

## Execution Plans

Planned plan types:

- InsertPlan
- ReadPlan
- UpdatePlan
- DeletePlan
- ValidationPlan
- MigrationPlan
- DiffPlan
- ExportPlan
- ImportPlan
- HealthPlan

Each plan is immutable and contains everything required for execution.

## Capability Negotiation

Before producing a plan, the Planner compares contract requirements with backend capabilities.

Examples:

- JSON support
- Transactions
- Unique indexes
- Generated columns
- Full text search

If a required capability is unavailable, planning fails with a PlanningError.

## Planner Invariants

1. Planning is deterministic.
2. Planning has no side effects.
3. Plans are immutable.
4. Planning never touches the database.
5. Planning is backend-aware.
6. Planning is independent of SQL generation.

## Interaction with Storage Strategies

The Planner selects the appropriate storage strategy based on the Persistence Contract.

```
InsertPlan
      │
      ▼
HybridStorage
      │
      ▼
SQLAlchemyBackend
```

The strategy translates the plan into backend-specific operations.

## Error Handling

Possible errors:

- PlanningError
- UnsupportedBackendError
- CapabilityMismatchError
- InvalidContractError

## Testing

Planner tests should verify:

- Deterministic plans.
- Correct capability negotiation.
- Stable plan generation.
- No database access during planning.

## v0.1 Scope

Included:

- InsertPlan
- ReadPlan
- UpdatePlan
- DeletePlan
- ValidationPlan

Deferred:

- Bulk optimization
- Cost-based planning
- Adaptive planning
- Plugin optimization

## North Star

The Planner separates *what* should happen (Persistence Contract) from *how* it happens (Execution Plan), allowing ModelVault to remain declarative, testable, and backend-independent while leveraging trusted databases.
