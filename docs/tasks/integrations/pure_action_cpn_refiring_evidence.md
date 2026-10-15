# Experimental pure-action CPN refiring evidence

## Scope

This record covers one bounded, in-memory, canonical pure-CPN replay transcript
and exact refiring verifier. It extends compact structural replay with semantic
CPN reconstruction while remaining separate from durable history retention and
complete runtime safety-state replay.

## Implemented boundary

- `ExperimentalWorkflowPureActionCpnReplayBundle` content-identifies the exact
  candidate CPN-plan and input-plan identities, retained execution profile,
  canonical definition bytes, canonical predecessor and successor marking
  bytes, transition, selected binding, optional directed-selection identity,
  external-output binding, and expected firing-result identity.
- Bundle construction accepts only an exact successful
  `ColoredPetriNetFiringResult`, verifies it through pure refiring, and requires
  its definition bytes to match the retained CPN plan exactly.
- Bundle construction reconstructs the complete candidate CPN-plan identity from
  the retained input-plan identity, definition representation, and execution
  profile. A profile substitution cannot remain attached to the earlier plan
  identity.
- `ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec` uses one closed,
  bounded, canonical UTF-8 JSON schema. Exact canonical definition and marking
  bytes use strict padded Base64; generic CPN bindings use closed tagged values
  and preserve definition-owned assignment order.
- `ExperimentalWorkflowPureActionCpnReplayService` accepts canonical bytes,
  rejects unsupported retained execution profiles as `INCOMPATIBLE`, rebuilds
  enablement and deterministic or directed selection, constructs a fresh
  `ColoredPetriNetFiringInput`, invokes only the pure
  `ColoredPetriNetTransitionFirer`, and compares the complete firing-result
  identity and successor marking.
- Closed replay outcomes are `REPLAYED`, `INCOMPATIBLE`, `CORRUPT`, and `ERROR`.
  The service has no owner firer, SDK request/result codec, source repository,
  artifact resolver, persistence adapter, clock, filesystem, or network
  dependency.
- The transcript contains generic CPN state and opaque logical identity values;
  it contains no owner payload body, artifact document, private locator, or
  native file.

## Adversarial evidence

Focused tests prove:

- canonical bundle encode/decode/re-encode and deterministic successful refiring;
- owner call count does not change during replay;
- retained directed selection is reconstructed from its exact derived directive;
- changed expected result identity, external-output binding, or successor body
  fails as `CORRUPT`;
- an unsupported but internally consistent retained plan/profile returns
  `INCOMPATIBLE`;
- profile substitution under an unchanged CPN-plan identity is rejected;
- unknown fields, unsupported transcript schema, invalid Base64, changed bundle
  identity, noncanonical whitespace, and non-byte inputs fail closed; and
- the provenance-bound shadow CPN sources remain unchanged.

The deterministic fixture bundle identity is
`60ca7e19c47bc8026f178fb97a79f9f9fd8348d38e3f6a1118dc71229ae3d5da`.
Its 4,516-byte canonical transcript SHA-256 is
`d001410c1f5888d2d31d4a8a81960cbb571b3064d9f51cc9f491be20f0c4b7e4`.

## Validation

Validation from the uncommitted candidate on Workflow revision `4b9a5e1`:

- full Workflow suite: `406 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `59` production source files;
- Ruff, changed-source formatting, architecture/documentation checks, runtime
  dependency boundary, shadow provenance, and `git diff --check`: passed;
- two Workflow wheels built with the same `SOURCE_DATE_EPOCH` were
  byte-identical, SHA-256
  `e8e4467b7b50cd6e0ae21a24c73fbbf2798ac76bbcaa924075271988d8e18b6a`;
- the clean Workflow wheel installed with the standalone SDK wheel and imported
  the public replay-bundle factory, codec, and pure refiring service.

Artifact SHA-256 values:

- canonical transcript and refiring implementation:
  `afc773fc289f0aa92890cf018e2e8b193ef94e09255d4821e98b8dfac2789b6e`;
- focused transcript/refiring tests:
  `6686513a06da9094bb4af8b169661ab9c7d7328d1f6fdd514b356604f306ae84`.

## Remaining gaps

The replay bundle is not durably retained or atomically linked to the compact
commit. It does not reconstruct SDK request/result history, source-authority
observations, reservation lifecycle, or the complete runtime safety state. It
therefore must not be described as complete committed replay or complete
CPN-bindings conformance.

Before adding a SQLite replay-evidence schema or another SQLite adapter, the
[private SQLite boundary consolidation task](../tech_debt/consolidate_sqlite_private_database_boundary.md)
reached its revisit condition and now has completed organization evidence.
Durable replay work may next retain a content-addressed bundle reference without
embedding CPN definitions or marking bodies in the compact commit event.
