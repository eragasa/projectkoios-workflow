# Pure-action reservation lifecycle evidence

## Scope

This record covers a bounded v0, identity-only durable reservation lifecycle. It
adds no owner payload retention and does not claim complete SDK request/result
history or runtime safety-state replay.

## Implemented boundary

- `ExperimentalWorkflowPureActionReservationLifecycleEvent` binds the complete
  reservation record to either `RESERVED` or `COMMITTED`; committed events also
  bind the exact compact-commit identity.
- The strict canonical JSON codec uses a closed schema, exact built-in types,
  bounded UTF-8 bytes, and byte-exact decode/re-encode validation.
- SQLite format version 4 stores ordered canonical lifecycle events with typed
  columns and event digests.
- Reservation acceptance atomically retains the reserved event. Commit
  acceptance atomically retains the committed event with compact commit, replay
  evidence, reservation consumption, and marking advancement.
- Atomic lifecycle reads distinguish `FOUND`, `LEGACY_PARTIAL`, `ABSENT`,
  `INCOMPATIBLE`, `CORRUPT`, and `ERROR`.
- Version-3 active reservations migrate to complete reserved lifecycles.
  Consumed version-3 reservations lack reconstructable reservation fields and
  migrate only to explicit `LEGACY_PARTIAL` records; no missing field is
  fabricated.
- Structural lifecycle replay loads only the durable identity transcript and
  invokes no owner, source repository, owner codec, or CPN firer.

## Adversarial evidence

Focused tests cover canonical codec rejection, reserve/commit reconstruction,
owner and source non-invocation, active and consumed v3 migration, migration
rollback, commit rollback, corruption, absence, reopen, and existing concurrent
idempotence behavior. The deterministic reserved-event identity is
`96e3d79d7302ea84ed636977d0489e45c24dcc8d31542a98da6e4f67156c5765`;
its 1,180 canonical bytes have SHA-256
`ceb3ed60763d291a5ee345a5d4788d71d61b4c33c69798de6391e1b7531786fb`.

## Validation

- Ruff and changed-source formatting: passed.
- Strict mypy: passed over 75 production source files.
- Workflow suite: 426 passed.
- Standalone SDK suite: 13 passed.
- Architecture, runtime-dependency, and shadow-provenance checks: 7 passed.
- Two Workflow wheels were byte-identical, SHA-256
  `32d41dc33dc1bd87434084b5233e6cb3ecce02ae7ae5ea14a64226e9341f8eb2`.
- A clean environment installed the Workflow and standalone SDK wheels and
  imported the public lifecycle event, codec, nominal repository, replay
  service, and SQLite implementation.

Artifact SHA-256 values:

- lifecycle records, codec, port, and replay service:
  `fa0efe967d907832bba5014a084a042cf0146598708567362d355007a09c1a3c`;
- lifecycle SQLite row codec:
  `183a65ce7edddfcf55de7de3d02dd28e9a3ff3a8b3198681b14c7eb8089b45ce`;
- exact schema and transactional migrations:
  `6adb0c75a414cbc7c3876b22c44b20e9769d31799792a9eaad93e1f5534f511a`;
- evolved SQLite transaction orchestrator:
  `64e50211ab2c8a64e1c532050fa40f435ad59e7349686d84aef3b89fce093c91`;
- focused lifecycle tests:
  `f02213647b20b8c3600616a3c85d556d3f74fb51dfa5e530523dd6648a101da4`.

## Remaining limits

Complete SDK request/result payload reconstruction remains blocked on an
owner-controlled immutable evidence-retention design because Workflow must not
persist owner payload bodies. Source revalidation and predecessor commit remain
sequential across nominal repositories. Compact-only writing remains legacy
compatibility behavior rather than the recommended authoritative path.
