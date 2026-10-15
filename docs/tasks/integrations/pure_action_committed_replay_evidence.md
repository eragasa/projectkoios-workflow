# Experimental pure-action committed-replay evidence

## Scope

This record covers strict canonical serialization and read-only structural replay
of one durably committed v0 pure-action compact record. Replay reconstructs the
compact commit identity and predecessor/successor coordinates without invoking
the owner integration or the CPN kernel.

This is not complete CPN-bindings replay. It does not decode retained CPN
definitions or markings, re-execute a retained execution profile, replay the
pure transition firing, resolve owner payloads, or reconstruct the complete
runtime safety state.

## Implemented boundary

- `ExperimentalWorkflowPureActionCommitEventJsonCodec` encodes one closed,
  bounded, identity-only UTF-8 JSON schema with deterministic key ordering and
  no insignificant whitespace.
- Strict decoding rejects noncanonical JSON, unknown or missing fields,
  unsupported schema identities, invalid built-in types, invalid nominal
  identities, changed source-authority identity derivations, excess bounds, and
  non-UTF-8 bytes.
- The durable SQLite repository stores the exact canonical event bytes beside
  its purpose-built typed columns and ordered source-authority references. The
  event binds the exact net instance. One closed snapshot read returns the
  decoded record, full coordinates, and exact bytes from one observation and
  requires them and the integrity digest to agree exactly.
- `ExperimentalWorkflowPureActionCommittedReplayService` consumes only that
  retained snapshot. It reconstructs `ExperimentalWorkflowPureActionCommit`,
  recomputes its existing semantic identity, verifies net instance and complete
  predecessor/successor coordinates, returns those coordinates, and preserves
  closed `REPLAYED`, `ABSENT`, `INCOMPATIBLE`, `CORRUPT`, or `ERROR` outcomes.
- Replay has no worker integration, `Firer`, owner/source repository, owner
  codec, artifact resolver, CPN definition, marking body, or
  `ColoredPetriNetTransitionFirer` dependency at execution time.
- Owner payload bodies, private locators, artifacts, and native files remain
  absent from both the canonical event and durable schema.

## Adversarial evidence

Focused tests prove:

- canonical encode/decode round trips are deterministic;
- whitespace-prefixed and unknown-field JSON is rejected;
- a changed source-authority identity is rejected even when the JSON is
  otherwise canonical;
- durable reopen returns byte-exact canonical event bytes and full coordinates;
- cross-net event/coordinate substitution is rejected;
- durable corruption and incompatible schema versions retain distinct closed
  replay outcomes;
- compact replay reproduces the existing deterministic commit identity;
- owner firer call count does not change during either in-memory or durable
  replay;
- absent commits return a closed absence rather than causing owner execution;
- disagreement between durable typed columns and event bytes fails closed.

## Validation

Validation from the uncommitted candidate on Workflow revision `5ff9c3a`:

- full Workflow suite: `385 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `56` production source files;
- Ruff, changed-source formatting, architecture/documentation checks, runtime
  dependency boundary, shadow provenance, and `git diff --check`: passed;
- two Workflow wheels built with the same `SOURCE_DATE_EPOCH` were
  byte-identical, SHA-256
  `61c43e5d7d4561280814ba62ef7060fecbd2c93bbf3cb5865da95a7fc62a7b6e`;
- the clean wheel installed with the local SDK wheel and imported the canonical
  event codec and committed replay service successfully.

Artifact SHA-256 values:

- canonical committed-event codec:
  `a68361fe897f32b594ad10cfd1a8c7c84dd249d1398c0480162a460266bbdf85`;
- read-only compact replay service:
  `c95b8d82160f2648ee84fcfcba4e3995eca61db37e9c3957428715948aa0f6ee`;
- evolved durable SQLite repository:
  `35d7a4f883c6d93f6c5e9ddc2c8fe0ed64742b8554c40dcaf47ee4624f96bb3b`;
- focused committed replay tests:
  `d9c9d27ec9c3374caced56786a5fe5211f5cc6caafe9825b78f48d753920055e`;
- evolved durable persistence tests:
  `7420294c9fc469f4a7cabb0c27bd40c45da9d2d62cc765fd882e8f79095715d5`.

The replayed compact commit identity remains
`b58cbaf0c02fabf51c9d635bfbc8d6ecbcec6c1358e7e09580eb2544cf40e626`.

## Remaining gaps

A later bounded follow-up now provides canonical CPN definition and semantic
marking decoding, but complete replay still requires retention and loading of
the exact representation bundle, retained execution-profile support validation,
pure CPN refiring, audit and successor comparison, complete
request/result/evidence history, and runtime safety-state reconstruction.
Missing retained representations must continue to fail closed; this structural
replay must not be relabeled as complete semantic or CPN replay.
