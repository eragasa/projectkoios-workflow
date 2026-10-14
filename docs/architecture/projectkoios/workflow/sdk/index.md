# `projectkoios.workflow.sdk` architecture

> **Status: authorized and implemented standalone `0.1.0a1` package, public
> type inventory, canonical encoding, and Workflow self-consumption; the
> owner-backed vertical slice remains pending.** No external owner is authorized
> to depend on the SDK until the remaining readiness gates are accepted.

## Responsibility

The SDK is the candidate stable dependency surface for external definition,
action, descriptor, and worker integration packages. It owns frozen slotted
records, nominal runtime-enforced ABCs, and reusable validating bases. It
contains no scheduler, database, API server, control-plane plugin discovery, or
domain implementation.

Workflow owns the common `Firer` ABC used only for Workflow integrations.
Consumer repositories encapsulate that boundary in their own integration ABCs
and retain ownership of domain requests, results, codecs, identities, and
validation. The common integration firer is distinct from the pure
`ColoredPetriNetTransitionFirer` that constructs successor markings.

After acceptance, external owners may use the SDK to describe CPN source
bindings and expose typed actions without gaining access to a mutable marking.
Until then, owner repositories should continue producing runtime-neutral typed
actions under accepted local contracts and supply pinned fixtures for adapter
review.

## Authorized packaging baseline

The operator authorized this initial packaging direction:

- source repository: `projectkoios-workflow`;
- separate build root: `sdk/`;
- distribution: `projectkoios-workflow-sdk`;
- public import root: `projectkoios.workflow_sdk`;
- initial target version: `0.1.0a1`;
- runtime dependencies: Python standard library only;
- runtime extension enforcement: nominal ABCs, not structural protocols; and
- initial scope: pure firing only, with external-effect lifecycle deferred.

The separate import root avoids splitting ownership of the existing
`projectkoios.workflow` package across distributions. Packaging authorization
does not accept public class names, record fields, serialization, compatibility,
consumer migration, release, or deployment.

SDK compatibility is versioned independently from service internals so provider
releases do not require lockstep changes to Laptop, Web, or generic API adapters.

## Authorized alpha surface

The exact authorized module, class, field, result-variant, and exclusion
inventory is recorded in [`public_api.md`](public_api.md). The authorized strict
canonical JSON encoding is recorded in
[`serialization.md`](serialization.md). The selected long-term separation
between an owner logical-identity output and full-document evidence belongs to
the SDK [transition action binding](actions/TransitionActionBinding/), while
runtime admission and atomic firing belong to
[`WorkflowEngine`](../runtime/WorkflowEngine/). This direction does not add a
`0.1.0a1` public symbol or claim that CPN admission is implemented. These
records do not by themselves authorize external release, production use, or
completion of the remaining vertical-slice gates.
