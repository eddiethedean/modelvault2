# DESIGN_PRINCIPLES.md

# ModelVault Design Principles

> **Every architectural decision in ModelVault should be explainable by these principles.**

These principles are intentionally stable. APIs, internal implementations, and supported backends may evolve, but the principles should change rarely. They are the constitution of the project.

---

# 1. Models Are the Source of Truth

Application models define the domain.

Database schemas, metadata, repositories, and migrations are derived artifacts.

Never require developers to maintain multiple competing definitions of the same model.

---

# 2. Persistence Contracts Are the Source of Persistence

A Pydantic model describes **what** data is valid.

A Persistence Contract describes **how** that data should live in storage.

Contracts are explicit, versioned, inspectable, and deterministic.

---

# 3. Trust Existing Databases

ModelVault will never compete with SQLite, PostgreSQL, DuckDB, or other mature databases.

Those systems own:

- durability
- transactions
- indexing
- concurrency
- recovery
- query execution

ModelVault owns model integrity.

---

# 4. Boring Underneath, Powerful Above

Innovation belongs in the model layer—not in storage engines.

The implementation should leverage mature, well-tested infrastructure while exposing a higher-level model-centric experience.

---

# 5. Read Validation Is a First-Class Feature

Validation does not stop at writes.

Every record loaded through ModelVault should be validated against its contract by default.

This catches:

- schema drift
- serialization bugs
- corrupted records
- stale data
- manual database edits

---

# 6. Contracts Are Immutable

A Persistence Contract represents a specific version of persistence behavior.

When persistence behavior changes, a new contract is created.

Historical contracts remain inspectable.

---

# 7. Explicit Over Magical

ModelVault should avoid hidden behavior.

Developers should understand:

- what metadata is created
- what tables exist
- what indexes are expected
- why migrations are required
- how validation occurs

---

# 8. Zero Vendor Lock-In

User data belongs to the user.

If ModelVault is removed, the underlying database remains usable with standard SQL tools.

No proprietary storage format should be required.

---

# 9. Backend Portability

Applications should move between supported backends with minimal application changes.

Backend differences should be acknowledged explicitly rather than hidden.

---

# 10. Metadata Is a Feature

Metadata is not an implementation detail.

It enables:

- discovery
- inspection
- health reporting
- schema history
- migration planning
- operational confidence

Metadata should be human-readable and queryable.

---

# 11. Execution Is Planned

ModelVault does not execute operations directly from models.

Operations are derived from Persistence Contracts into execution plans.

Examples:

- InsertPlan
- ReadPlan
- ValidationPlan
- DiffPlan
- MigrationPlan

Planning makes behavior predictable, inspectable, and extensible.

---

# 12. Collections Are Facades

Collections provide the public API.

They coordinate contracts, planners, storage strategies, and backends.

They should remain intentionally small and easy to understand.

---

# 13. Small Public API

The public API should remain compact.

A developer should accomplish most work through:

```python
vault = Vault(...)
users = vault.collection(User)

users.insert(...)
users.get(...)
vault.health()
```

Complexity belongs in internal components.

---

# 14. Composition Over Inheritance

ModelVault should compose behavior from:

- contracts
- planners
- storage strategies
- backends
- plugins

Avoid deep inheritance hierarchies.

---

# 15. Observable Systems

Everything important should be inspectable.

Developers should be able to answer:

- What contract is active?
- What schema version is stored?
- Why did validation fail?
- Is drift present?
- What migration is required?

without reading internal source code.

---

# 16. Backend Capabilities Must Be Honest

ModelVault should never silently degrade guarantees.

If a contract requires a backend capability that is unavailable, registration should fail with a clear explanation.

---

# 17. Progressive Complexity

Simple applications should remain simple.

Advanced capabilities—custom serializers, plugins, multiple contracts, advanced migrations—should be opt-in.

---

# 18. Prefer Determinism

Schema fingerprints, execution plans, metadata, and generated artifacts should be deterministic.

The same inputs should always produce the same outputs.

---

# 19. Optimize for Long-Term Maintenance

Readable architecture is more valuable than clever implementation.

Favor clear boundaries, stable interfaces, and comprehensive documentation over premature optimization.

---

# 20. The North Star

Every proposed feature should answer one question:

> **Does this make application models more trustworthy while keeping storage grounded in databases developers already trust?**

If the answer is yes, it likely belongs in ModelVault.

If the answer is no, it should be reconsidered.
