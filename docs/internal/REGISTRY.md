# REGISTRY.md

# Contract Registry

## Purpose

The Registry is the persistent catalog of ModelVault contracts.

It allows a database to explain which models it stores, which contract versions exist, and whether runtime models match stored metadata.

## Responsibilities

The Registry owns:

- metadata table creation
- contract persistence
- schema history
- model listing
- basic drift detection
- validation event recording

The Registry does not own:

- application CRUD
- SQL table generation for model records
- validation execution
- execution planning

## v0.17 Metadata Tables

### modelvault_registry

Stores current contract metadata.

Columns:

```text
collection_name TEXT PRIMARY KEY
model_name TEXT NOT NULL
python_path TEXT NOT NULL
table_name TEXT NOT NULL
storage_mode TEXT NOT NULL
key_field TEXT NOT NULL
contract_hash TEXT NOT NULL
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

### modelvault_schemas

Stores contract schema snapshots.

Columns:

```text
id INTEGER PRIMARY KEY AUTOINCREMENT
collection_name TEXT NOT NULL
contract_hash TEXT NOT NULL
schema_json TEXT NOT NULL
modelvault_version TEXT NOT NULL
fingerprint_version TEXT NOT NULL
created_at TEXT NOT NULL
```

### modelvault_validation_events

Stores validation failures.

Columns:

```text
id INTEGER PRIMARY KEY AUTOINCREMENT
collection_name TEXT NOT NULL
record_key TEXT
direction TEXT NOT NULL
status TEXT NOT NULL
error_json TEXT
created_at TEXT NOT NULL
```

## Registry API

Required:

```python
ensure_metadata()
register_contract(contract)
get_contract(collection_name)
list_contracts()
record_validation_event(...)
detect_drift(contract)
```

## Registration Behavior

When registering a contract:

1. Ensure metadata tables exist.
2. Compute contract hash.
3. Check if collection exists.
4. If new, insert registry and schema rows.
5. If existing and hash matches, no-op.
6. If existing and hash differs, report drift.

v0.17 should not automatically migrate changed contracts.

## Drift Detection

Drift exists when runtime contract hash differs from stored contract hash.

Return:

```python
DriftReport(
    collection_name="users",
    stored_hash="...",
    current_hash="...",
    status="drift_detected",
)
```

## Registry Invariants

- Registry tables are ordinary SQL tables.
- Registry metadata is inspectable with SQL.
- Contract hashes are deterministic.
- Historical schema rows are append-only.
- Registry does not silently overwrite changed contracts.
- Drift must be reported explicitly.
