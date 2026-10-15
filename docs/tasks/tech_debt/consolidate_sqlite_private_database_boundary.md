# Consolidate the private SQLite persistence boundary

## Problem

`persistence/sqlite.py` and `persistence/pure_action_sqlite.py` independently
implement private path validation, symlink rejection, connection setup, pragma
enforcement, transaction entry, and exception translation. The pure-action
adapter also combines schema orchestration and row reconstruction in one large
module. The duplication is currently tested and fail-closed, but another schema
or adapter can cause security-policy and corruption-classification drift.

The new in-memory CPN replay candidate deliberately adds no SQLite schema. Its
model, canonical transcript serialization, and replay orchestration currently
share one bounded module; durable transcript retention would expand all three
concerns and should not be added without separating them.

## Activation condition

This task is required before adding a durable CPN replay-transcript table,
another SQLite adapter, or a schema migration. That condition is now the next
step after the in-memory CPN refiring candidate.

## Action

- [x] Inventory exact path, ownership, no-follow, connection, pragma, timeout,
  transaction, rollback, and close behavior in both SQLite adapters.
- [x] Extract one internal private-database path and connection policy without
  weakening either adapter's existing rejection behavior.
- [x] Separate pure-action SQLite row decoding and integrity classification from
  transaction orchestration.
- [x] Split CPN replay bundle models, canonical serialization, and refiring
  orchestration before adding durable transcript rows.
- [x] Preserve existing public repository ABCs, identity domains, canonical
  bytes, corruption outcomes, and deterministic vectors.
- [ ] Add the durable replay-evidence schema only as a later separately reviewed
  slice.

## Required evidence

- [x] Existing SQLite and replay tests remain unchanged or stronger.
- [x] Symlink, permissions, incompatible-version, corruption, rollback, reopen,
  crash, and concurrency evidence remains passing.
- [x] Row corruption remains distinguishable from database operational errors.
- [x] No owner payload, artifact document, private locator, CPN definition, or
  marking body enters the compact commit event.
- [x] Ruff, formatting, strict mypy, full tests, architecture boundaries,
  provenance, reproducible build, and clean-wheel import checks pass.

This task authorizes organization and policy consolidation only. It does not
itself authorize a schema migration or claim durable complete replay.

The completed organization slice has separate
[validation evidence](sqlite_private_boundary_consolidation_evidence.md).
