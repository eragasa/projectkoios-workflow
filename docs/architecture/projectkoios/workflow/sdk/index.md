# `projectkoios.workflow.sdk` architecture

> **Status:** standalone SDK `0.1.0a1` and its pure `Firer` surface are
> implemented and exercised by a real Simulations owner vertical slice. The
> iteration-2 Task/Workflow source model is proposed and is not part of that
> public API.

## Responsibility

The SDK is the candidate stable dependency surface for owner integrations. It
owns frozen slotted records, nominal runtime-enforced ABCs, canonical pure-firing
transport, and reusable validating template methods. It contains no scheduler,
database, service registry, compiler, CPN implementation, owner semantics, or
domain payload repository.

Workflow owns the common `Firer` ABC for one pure atomic Task execution.
Consumers encapsulate it in owner-specific nominal ABCs and retain their typed
requests, results, codecs, identities, scientific semantics, and provider
specializations. `Firer` remains distinct from
`ColoredPetriNetTransitionFirer`, which computes CPN successors.

Architecture iteration 2 proposes a later nominal source-language `Task` and
`Workflow(Task)` relationship. A parent contains Task instances; a
workflow-backed Task creates a distinct child run. Exact class names and fields
remain gated on Simulations QE/VASP evidence and one independent
`ksdft2effmass/experiments/` pilot. Nothing in that proposal changes the
`0.1.0a1` public inventory.

## Implemented packaging baseline

- source repository: `projectkoios-workflow`;
- separate build root: `sdk/`;
- distribution: `projectkoios-workflow-sdk`;
- public import root: `projectkoios.workflow_sdk`;
- current version: `0.1.0a1`;
- runtime dependencies: Python standard library only;
- runtime extension enforcement: nominal ABCs, not structural protocols; and
- implemented scope: pure firing only.

The SDK does not authorize effects, owner migration, release, or deployment.
SDK compatibility is versioned independently from service internals.

## Public surface and future source model

The exact implemented inventory is recorded in
[`public_api.md`](public_api.md), and canonical encoding in
[`serialization.md`](serialization.md). The future Task/Workflow authoring model
is described under [`source/`](source/) and remains architecture only.

The long-term separation between owner logical output and exact-byte evidence
belongs to [transition action binding](actions/TransitionActionBinding/).
Runtime admission, reservation, pure CPN firing, and atomic commit belong to
[`WorkflowEngine`](../runtime/WorkflowEngine/).
