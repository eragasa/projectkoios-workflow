# Pure-action durable CPN replay evidence validation

## Outcome

The bounded v0 candidate stores canonical CPN replay bundles separately from
compact commit state and atomically links them to accepted commits. Version-2
stores migrate transactionally; older compact commits remain replay-evidence
absent rather than acquiring fabricated transcripts.

## Preserved vectors

The existing canonical transcript and bundle identity tests remain unchanged:

- replay-bundle identity:
  `60ca7e19c47bc8026f178fb97a79f9f9fd8348d38e3f6a1118dc71229ae3d5da`;
- canonical 4,516-byte transcript SHA-256:
  `d001410c1f5888d2d31d4a8a81960cbb571b3064d9f51cc9f491be20f0c4b7e4`.

## Validation

- Ruff source and tests: passed.
- Strict mypy over 64 production source files: passed.
- Workflow tests: 414 passed.
- Focused durable replay tests cover exact reopen, legacy absence, concurrent
  idempotence, injected precommit rollback, successful v2 migration, failed
  migration rollback, corruption classification, and pure CPN refiring; the
  existing SQLite process-crash recovery test also remains passing.
- Standalone SDK tests: 13 passed.
- Architecture, runtime-dependency, and shadow-provenance checks: 7 passed.
- Two Workflow wheels were byte-identical, SHA-256
  `3b6f403ec5590eac5844194a816a26b0ca8b56e1bd4c37816968aacd0fece880`.
- A clean environment installed the Workflow and standalone SDK wheels and
  imported the public durable replay port, service, and SQLite adapter.

Artifact SHA-256 values:

- durable replay evidence model, nominal port, and replay service:
  `4336add36e35aecbe18eba100484c5c20f696091fbb1a3635eda3a0d1df1389c`;
- evolved pure-action SQLite repository:
  `5dfed69521877b2cdc7b7fee5ef008e02a7e03159f75011ad9a32660e9429f0a`;
- focused durable replay-evidence tests:
  `939a66c35bf89d92a38fb889c66a58f8363a510409361939fa4abe7c203678a1`.

## Boundaries

Replay invokes no owner integration or source repository. Bundle bodies are not
embedded in compact event bytes. Complete runtime safety-state and
CPN-bindings replay remain explicitly unclaimed.
