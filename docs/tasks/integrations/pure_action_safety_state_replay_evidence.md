# Pure-action committed safety-state replay evidence

## Scope

This record covers bounded structural reconstruction of one committed v0
pure-action state from a single durable SQLite observation. It adds no schema,
owner payload retention, owner invocation, source resolution, or CPN firing.

## Implemented boundary

- `ExperimentalWorkflowPureActionSafetyStateSnapshot` correlates initial and
  current predecessor coordinates, the complete reservation lifecycle, compact
  committed snapshot, durable CPN replay evidence, and decoded predecessor and
  successor CPN markings.
- Snapshot validation rechecks net instance, reservation, request, input
  authorization, CPN plan, compact commit, firing result, predecessor, successor,
  and lifecycle correlations.
- The SQLite repository loads all components under one read transaction and
  verifies existing typed-column, canonical-byte, digest, and content-identity
  checks before returning a snapshot.
- Closed outcomes are `FOUND`, `LEGACY_PARTIAL`, `ABSENT`, `INCOMPATIBLE`,
  `CORRUPT`, and `ERROR`.
- Active reservations are absent from committed-state replay. Compact-only and
  migrated consumed histories remain explicitly partial rather than receiving
  fabricated replay evidence or lifecycle fields.
- Structural replay invokes no owner integration, source repository, owner
  codec, CPN binding selector, or CPN firer.

## Adversarial evidence

Focused tests cover exact successful reconstruction, owner/source
non-reinvocation, active-reservation absence, compact-only partial history,
migrated v3 partial history, replay-bundle corruption, and complete coordinate
and marking correlations. Existing migration, rollback, concurrency, canonical
codec, and provenance tests remain passing.

## Validation

- Ruff and changed-source formatting: passed.
- Strict mypy: passed over 77 production source files.
- Workflow suite: 430 passed.
- Standalone SDK suite: 13 passed.
- Architecture, runtime-dependency, and shadow-provenance checks: 7 passed.
- Two Workflow wheels were byte-identical, SHA-256
  `d8974031d1e0018ba88c18a4fa39dac3d5bee3658d58d0a8f98d6dbd4a661aad`.
- A clean environment installed the Workflow and standalone SDK wheels and
  imported the public safety-state snapshot, nominal repository, replay service,
  and SQLite implementation.

Artifact SHA-256 values:

- safety-state records, nominal port, and replay service:
  `6e000d3feab37ac4062ae7e508ff754ac5b7eeba1b0cbae4328566c8014f530c`;
- evolved SQLite repository:
  `75553cd9d9e51de8a2f6ffe479d10c09aef263e7d81c6265a194a4dbef8e9154`;
- focused safety-state replay tests:
  `49e0b2326361eeb39418056b114b7905095166f9d7c8507237f0a52f11c7beaf`.

## Remaining limits

This is one committed action snapshot, not a global scheduler state, complete
multi-occurrence runtime replay, or complete CPN-bindings conformance. Exact SDK
request/result payload history remains blocked on an owner-controlled immutable
evidence-retention design.
