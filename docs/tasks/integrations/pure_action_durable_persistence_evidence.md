# Experimental pure-action durable-persistence evidence

## Scope

This record covers the bounded v0 durable SQLite implementation of the nominal
pure-action reservation repository. It persists the complete compact commit and
ordered admitted source-authority references in the same transaction that
consumes the reservation and advances the marking coordinate.

It does not claim complete `WorkflowExecutionPlan` conformance, canonical
committed-event serialization, semantic committed replay, production backup or
migration readiness, or acceptance of the proposed CPN-bindings contract set.

## Implemented boundary

- `ExperimentalWorkflowPureActionCommitRecord` carries every compact commit
  field plus ordered source-authority reference, revision, and evidence
  identities. It carries no owner payload body, artifact, private locator,
  repository object, CPN definition, or marking body.
- `ExperimentalWorkflowPureActionCommitService` supplies that record to the
  nominal repository at the existing atomic commit boundary.
- `ExperimentalSQLitePureActionReservationRepository` uses a purpose-built
  SQLite schema for immutable initial predecessors, current predecessors, active
  reservations, consumed reservation identities, commits, and ordered source
  authorities. It does not encode the state into the older opaque revision
  table.
- Reservation and commit use `BEGIN IMMEDIATE`, full synchronous durability,
  foreign keys, rollback-journal mode, exact idempotency, bounded lock waiting,
  and private no-follow path checks.
- One commit transaction verifies the exact active reservation and predecessor,
  inserts the complete compact record and ordered evidence references, consumes
  the reservation, removes it from the active set, and advances the successor
  marking revision.
- Exact commit replay is idempotent after reopen. Concurrent exact commits yield
  one commit and one idempotent replay; concurrent distinct commits yield one
  commit and one conflict.
- Reservation semantic identities, predecessor coordinate digests, source
  authority identities, and complete commit-record digests fail closed on
  changed retained state.
- The commit and reservation status sets now preserve explicit `ERROR` and
  `INDETERMINATE` outcomes where a durable operation cannot make a safe success
  claim.

## Recovery and rollback evidence

Focused tests prove:

- committed coordinates and the complete record reconstruct after reopening;
- a separately launched Python process can begin and mutate a marking
  transaction and exit through `os._exit` without commit, after which reopening
  recovers the prior marking and current reservation;
- an injected exception immediately before SQLite commit rolls back commit rows,
  source-authority rows, reservation consumption, and marking advancement;
- digest-corrupted compact commits and current predecessors fail closed;
- changed bootstrap state fails closed;
- symlink database files are rejected, database and parent modes remain private,
  and no WAL or shared-memory sidecars are created;
- the end-to-end commit service writes the same deterministic compact commit
  identity through the durable repository.

## Validation

Validation from the uncommitted candidate on Workflow revision `4b4ea69`:

- focused durable repository tests: `11 passed`;
- focused end-to-end durable commit-service test: `1 passed`;
- full Workflow suite: `379 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `54` production source files;
- Ruff, changed-source formatting, architecture/documentation checks, runtime
  dependency boundary, shadow provenance, and `git diff --check`: passed;
- two Workflow wheels built with the same `SOURCE_DATE_EPOCH` were
  byte-identical, SHA-256
  `200968fa71feb34cb8428059824955885727e38be8fba0e6006ceb1da24dba4f`;
- the clean wheel installed with the local SDK wheel and imported the durable
  repository and compact commit record successfully.

Artifact SHA-256 values:

- durable SQLite repository:
  `a0561c5254e9b8673ac12a4e45c2b95a5de3dbc3c9dd4c4a4b7d84d30e5a0d3f`;
- evolved reservation records and repository boundary:
  `6cbcb50ba5e0f0e8d2d710e83f80c2d5bc459c8fb79c6cf1b9f0c160493a83ec`;
- evolved atomic commit service:
  `592e892d173827c172d9d5d5620aa6f59a3526bd814cbb373cbf89f3f14e3eb0`;
- focused durable repository tests:
  `ca1820104b14250656144e6cad2b7ed06b6c221e7f5481a27497fc1d4088dc5b`;
- focused atomic commit tests:
  `ab3a3e6a0fc47cca9a19dd22a12bdaba4c0128130e4cbf8776bb7b74548d7125`.

The successful vertical fixture preserves compact commit identity
`b58cbaf0c02fabf51c9d635bfbc8d6ecbcec6c1358e7e09580eb2544cf40e626`.

## Remaining gaps

Canonical committed-event serialization and read-only committed replay without
owner reinvocation remain unimplemented. The repository exposes fail-closed
exceptions for compact read corruption because the inherited v0 read methods do
not yet have closed read-result records. Production backup, schema migration,
monitoring, and recovery operations remain outside this candidate.

Source revalidation and SQLite commit remain sequential across nominal
repositories rather than one distributed transaction. A production owner source
adapter must guarantee revision immutability to close that observation race.
