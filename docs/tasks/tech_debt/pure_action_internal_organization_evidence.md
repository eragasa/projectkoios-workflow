# Pure-action internal organization evidence

## Scope

This evidence covers the authorized maintainability-only refactoring of the
experimental pure-action vertical slice. It does not change public records,
identity domains, canonical preimages, rejection outcomes, SDK contracts, or
shadow-CPN sources.

The slice:

- consolidates authorized-input, successful-reservation, canonical-request, and
  CPN-plan reconstruction under `projectkoios.workflow.execution._validation`;
- keeps invocation and firing outcome reconstruction with their defining phase
  modules and reuses it from later phases;
- separates canonical CPN definition representation identity, encoding, and
  representation-byte inspection from plan/profile models;
- splits the former reservation test module into shared fixtures and bounded
  input, reservation, invocation, firing, and commit modules.

Canonical semantic CPN definition decoding remains unimplemented. The broader
admitted transition/firer contract and serialization-count work remains open.

## Preserved evidence

The complete test suite preserves all `47` focused pure-action cases, including
source and predecessor staleness, direct forgery, owner mutation and exceptions,
CPN rejection, definition substitution, concurrent commit, rollback, and exact
commit replay. The deterministic compact commit identity remains
`b58cbaf0c02fabf51c9d635bfbc8d6ecbcec6c1358e7e09580eb2544cf40e626`.

The provenance test confirms that the shadow CPN production sources and
transformed tests remain byte-identical to
`provenance/colored-petri-net-shadow.json`.

## Validation

- focused pure-action slice: `47 passed`;
- full Workflow suite: `367 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `53` production source files;
- Ruff lint, changed-source formatting, documentation/architecture tests,
  runtime dependency boundary, shadow provenance, and `git diff --check`: passed;
- two Workflow wheels built with the same `SOURCE_DATE_EPOCH` were
  byte-identical, SHA-256
  `945c9f27df82fa3133d1b29582e479fcd55e5191a25768dd2f783a7ce79842f1`;
- the clean wheel installed with the local SDK wheel and imported the public CPN
  encoder and atomic commit service successfully.

Artifact SHA-256 values:

- execution validation module:
  `22337a5485f256e6777bcc1911c2bf2d22332db567160262c8d1dd88237d058d`;
- CPN representation module:
  `c3e23c9f9f00a6e2db40e5b9ae10ca8563bbb6873bd97c855e236286219158e5`;
- shared pure-action fixture module:
  `af9858776aa16b76c11a42e6f300d7917e2a11cc94e81526254b927a0f8e4db0`.
