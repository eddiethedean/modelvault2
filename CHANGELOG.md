# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.17.0] - 2026-06-25

### Added

- Public API: `Vault`, `@model`, and `ModelVaultError`
- SQLite backend via SQLAlchemy Core
- Table storage strategy for Pydantic v2 models
- Typed `Collection` CRUD: insert, upsert, get, delete, exists, count, all, find
- Write and read validation (strict by default)
- Persistence contracts with deterministic fingerprints
- Registry metadata tables (`modelvault_registry`, `modelvault_schemas`, `modelvault_validation_events`)
- Basic drift detection when stored contracts change
- `vault.health()`, `vault.describe()`, and `vault.models()`
- Sphinx documentation and Read the Docs configuration

### Notes

- v0.17 supports `storage="table"` only
- PostgreSQL, DuckDB, async, hybrid/document storage, and CLI are planned for later releases

[0.17.0]: https://github.com/eddiethedean/modelvault2/compare/v0.16.0...v0.17.0
