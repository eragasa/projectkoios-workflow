# Durable-history internal organization evidence

## Scope

This behavior-preserving prerequisite prepares the current v0 implementation
for complete request/result and reservation-lifecycle history. It adds no schema
migration, retained field, identity-domain change, canonical representation, or
new runtime behavior.

## Implemented organization

- Durable CPN replay SQLite row reconstruction, canonical evidence validation,
  bundle and association digest verification, and corruption faults moved to
  `_pure_action_cpn_replay_sqlite_rows`.
- `pure_action_sqlite` retains schema migration, query ordering, transaction,
  rollback, and closed read-outcome orchestration.
- Durable replay evidence records/factory, the nominal repository port, and the
  durable replay service moved to focused execution modules. The former module
  remains as a compatibility export surface.
- Reservation records/statuses, the nominal repository port, the in-memory
  implementation, and service orchestration moved to focused runtime modules.
  `pure_action_reservation` remains the stable compatibility export surface.
- Durable commit orchestration tests and SQLite replay-evidence persistence tests
  now use separate focused suites with shared typed fixtures.
- The compact-only and durable commit-writing semantics are intentionally
  unchanged; canonical-path retirement remains separate work.

## Preserved behavior

- Public imports and nominal class objects remain available.
- SQLite format version 3 and its version-2 migration are unchanged.
- Compact events, CPN replay bundles, identity preimages, read outcomes,
  rejection behavior, owner non-reinvocation, and shadow CPN provenance are
  unchanged.
- No owner payload, artifact document, or private locator enters compact state.

## Validation

- Ruff and changed-source formatting: passed.
- Strict mypy: passed over 73 production source files.
- Workflow suite: 420 passed.
- Standalone SDK suite: 13 passed.
- Architecture, runtime-dependency, and shadow-provenance checks: 7 passed.
- Two Workflow wheels were byte-identical, SHA-256
  `34e0e05b939800346a2ac350ece7969e07b63fd5760275aa5cbec43510fa0a34`.
- A clean environment installed the Workflow and standalone SDK wheels and
  imported the established public reservation, durable-commit, evidence-port,
  and replay types.

Representative artifact SHA-256 values:

- CPN replay SQLite row codec:
  `13647e7cad55740deb996f316b68f76a260a50bda783d844729d4bea0d4d0b87`;
- SQLite transaction orchestrator:
  `6cb122b1dbdceff48e4995109d6db5f655164293abc049502f7fee0a822f2303`;
- reservation compatibility exports:
  `b7e00d6cbc480874e80c79b4d5885588212d29c74c726648f207ff11af6d6177`;
- durable replay compatibility exports:
  `956da50c67cd03f319ba033c324c3c58559a25e1a96b328f0e5a7d074852187d`.

## Remaining limits

The legacy compact-only writer remains callable and must not become the default
for the authoritative vertical slice. Complete SDK request/result history,
reservation-lifecycle reconstruction, runtime safety state, and the documented
source-observation race remain outside this organization-only change.
