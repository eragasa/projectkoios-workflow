# `projectkoios.workflow.persistence` implementation

## Responsibility

The initial local deployment may use private SQLite plus a private content-addressed blob store. Preserve confinement, no-follow paths, ownership/mode checks, full durability, foreign keys, CAS, exact idempotency, corruption detection, and explicit indeterminate commit status from the current persistence prototype.

The production schema must be purpose-built rather than storing the whole platform in the existing opaque revision table. Backups require a drained, quiescent, schema-aware operation; state history is never rolled back.
