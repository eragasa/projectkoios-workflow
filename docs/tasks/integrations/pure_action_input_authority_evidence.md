# Experimental pure-action input-authority evidence

## Scope

This record covers a bounded Workflow-owned authority boundary for resolving
opaque input-source references through a nominal owner/source repository ABC. It
does not move owner artifacts or private payloads into Workflow persistence and
does not claim that the fixture repository is a production durable adapter.
The complete candidate remains v0 prerelease work; it introduces no v1, v2, or
v3 runtime contract.

## Implemented boundary

- `ExperimentalWorkflowPureActionInputSourceReference` content-identifies a
  bounded path-free source kind, source profile, and opaque source identity
  without carrying bytes or a private locator.
- `ExperimentalWorkflowPureActionInputSourceRepository` is a nominal ABC with
  closed `LOADED`, `ABSENT`, `INCOMPATIBLE`, `CORRUPT`, `INDETERMINATE`, and
  `ERROR` outcomes.
- A loaded result binds the exact source reference, source-owner revision/content
  identity, and reconstructed source evidence.
- `ExperimentalWorkflowPureActionInputAuthorizationService` validates the plan,
  selection, coordinates, and ordered source references before repository I/O,
  then constructs the SDK request only from loaded source bytes.
- `ExperimentalWorkflowPureActionAuthorizedInputs` closes the structural input
  admission and exact repository source observations under one identity.
- The reservation service reloads every source and compares its reference,
  revision, evidence, and bytes before reservation. Direct construction of an
  authorization record therefore grants no authority.
- The current v0 reservation identity binds the authorization identity. Earlier
  v0 experimental base and admission-bound shapes retain their original
  reconstruction domains.

Workflow retains bounded references and content identities; the source owner
continues to own private storage and retrieval semantics.

## Adversarial evidence

Focused tests cover absent, incompatible, corrupt, indeterminate, and error
source outcomes; source-kind/profile mismatch; caller-byte substitution;
changed source references and revisions; direct authorization forgery;
reservation-time source revalidation; stale and conflicting predecessor state;
and reconstruction of the earlier v0 reservation shapes.

Validation from the uncommitted candidate on base Workflow revision `6351a93`:

- focused input-authority/admission/reservation tests: `23 passed`;
- full Workflow suite: `343 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `46` source files;
- Ruff, formatting, architecture, shadow provenance, documentation-link, and
  diff checks: passed;
- source-repository boundary SHA-256:
  `20eefc4e10dfeca06207a5e1efcb546f89a7eaa4955c9b71d1a397703bacd556`;
- input-authorization source SHA-256:
  `658824d123b0d3608ee220dbf8702ddc72ff43fe504c65ddc228e50688a65768`;
- evolved reservation source SHA-256:
  `97f75c8427251e65f751bde66858cd9ddc655b0f7490c415f8c635faed3d2c81`;
- focused test source SHA-256:
  `f16f34b74aceaeca9a385afbefe011c853c6929c38cf15d668dabb408bf408f3`;
- two wheels built with `SOURCE_DATE_EPOCH=315532800` were byte-identical;
- wheel SHA-256:
  `40d8b1a4cbf4d423b21b7b5ba862e8c89a8f77c2989db1269ce8d6cb4fe998e7`;
- the wheel installed into the isolated Workflow/SDK/Simulations pilot
  environment, passed dependency checking, exposed the nominal source-authority
  boundaries, and preserved the existing plan, deployment-binding, and
  mapped-result identities.

Deterministic fixture identities:

- source reference:
  `22566bcce6c1dcbf961991ce2c86b4f6020ab0299eb275d7dce948a04d6da4b3`;
- source evidence/revision:
  `0b0485ea706bebe74d6ac980e046ec69e3b8f03106c75faea986e5edc16833e7`;
- authorized inputs:
  `567b0c136108d2920a6af69c9b70b7a36f7dd18bb60501513197a1dd978bc65c`;
- current v0 reservation:
  `c16c80412e269b5b2b717ce779cc210184ed5fd60873eb6c5cfb9d7293d0c313`;
- reconstructed v0 admission-bound reservation shape:
  `b25d1dbecb22b1f593c04d3713568ba3dc716b241a1b98121900323fd0d541e2`;
- reconstructed v0 base reservation shape:
  `2189a0d705aa0523585e434eaa6efc922bcdda1c7535e217c671776a23e9baf7`.

## Remaining gaps

The repository ABC has no production owner implementation in this repository.
The candidate does not invoke an owner firer, admit or map an SDK result, fire a
CPN transition, consume a reservation, persist a successor marking, or replay a
committed occurrence.
