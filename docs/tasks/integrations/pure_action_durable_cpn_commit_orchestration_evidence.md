# Pure-action durable CPN commit orchestration evidence

## Scope

This bounded v0 slice connects the validated invocation and pure-firing
candidate to the durable atomic CPN replay-evidence port. It changes no schema,
identity domain, compact-event encoding, replay-bundle encoding, or owner SDK
contract.

## Implemented path

- `ExperimentalWorkflowPureActionDurableCpnCommitService` accepts typed,
  already-authorized inputs, the exact successful reservation, CPN plan,
  invocation outcome, and firing outcome.
- The service reconstructs all trust-boundary records using the same preparation
  path as the legacy compact-only commit service.
- It constructs the replay bundle internally from the reconstructed plan and CPN
  firing result. Callers cannot supply arbitrary transcript bytes.
- The reservation service and replay-evidence port must own the exact same
  repository instance.
- Authoritative source observations are revalidated immediately before invoking
  the repository's atomic commit-with-replay operation.
- The durable repository commits compact state, canonical replay evidence,
  reservation consumption, and successor advancement in one transaction.
- Exact durable retries are idempotent. An earlier compact-only commit cannot be
  augmented after its accepted boundary and therefore conflicts rather than
  acquiring a post-commit transcript.
- Durable replay invokes only the pure CPN replay service; the owner call count
  remains unchanged.

## Adversarial evidence

Focused tests cover successful orchestration and durable refiring, exact
idempotence, owner non-reinvocation, source mutation, stale predecessor state,
repository substitution, legacy compact-commit conflict, injected transactional
rollback, reopen, concurrency, migration, and corruption behavior.

## Validation

- Ruff and changed-source formatting: passed.
- Strict mypy: passed over 65 production source files.
- Workflow suite: 420 passed.
- Standalone SDK suite: 13 passed.
- Architecture, runtime-dependency, and shadow-provenance checks: 7 passed.
- Two Workflow wheels were byte-identical, SHA-256
  `9e9566d51e1d7cf4e3fb9dd6c24faacfd079019014f7ca20f5ca9833df52d7c9`.
- A clean environment installed the Workflow and standalone SDK wheels and
  imported the public durable commit and replay services.

Artifact SHA-256 values:

- shared compact commit preparation:
  `137ab37f659e431dd227538e143c4b864df60434fdf65a0a4512038fd29826f4`;
- authoritative durable CPN commit service:
  `13ded734e8af969ba6b48a2af619da61874eef8c7332dd009a1a43b7ab524e49`;
- repository-instance ownership enforcement:
  `9c16c0e78e428ac7fd8f8a8d704efd05256db2a5ce141a46a54591bb32692c5e`;
- focused durable orchestration and persistence tests:
  `28d9b740d0bafe0374d80fbee6b6b2af8063c89af0fc9aeae98c84f14f4581f5`.

The established replay-bundle identity
`60ca7e19c47bc8026f178fb97a79f9f9fd8348d38e3f6a1118dc71229ae3d5da`
and canonical transcript SHA-256
`d001410c1f5888d2d31d4a8a81960cbb571b3064d9f51cc9f491be20f0c4b7e4`
remain unchanged.

## Remaining limits

Source revalidation and SQLite commit remain sequential across nominal source
and reservation repositories. Production source revision immutability must close
that observation race. Complete request/result history, reservation-lifecycle
reconstruction, and runtime safety-state replay remain outside this slice.
