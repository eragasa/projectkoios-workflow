# `WorkflowEngine`

> **Status: provisional architecture candidate.**

## Responsibility

`WorkflowEngine` coordinates one already compiled and linked plan against an
exact net instance. It accepts an exact selected binding or activation, derives
occurrence and attempt context, dispatches through the linked route, admits a
successful result, and requests atomic pure firing.

External-output admission is a Workflow runtime phase, not an SDK subsystem.
The engine obtains the pure candidate mapping from the linked
`TransitionActionBinding`, independently checks the exact SDK result and
retained deployment binding, revalidates the reserved predecessor and selected
CPN binding, and only then calls `ColoredPetriNetTransitionFirer`.

For the QE SCF artifact-set direction, the admitted CPN string is the opaque
Simulations-owned `artifact_set_identity`. The canonical `artifact_set` document
and its payload SHA-256 are retained as evidence and never substituted for that
logical identity.

The engine performs no discovery, registry lookup, plan inference, provider
selection, owner-domain import, or scientific interpretation. Rejected, failed,
or stale provider outcomes preserve evidence without fabricating a domain
firing.

A bounded experimental reservation candidate now closes one SDK request over
the exact plan/linking identities, structural selected-binding evidence,
plan-selected input-source evidence, predecessor coordinates, occurrence, and
attempt. It accepts no independent raw input tuple and re-resolves every source
through its nominal owner/source repository before reservation. Its nominal
predecessor-repository boundary supports atomic reservation and post-owner
revalidation; the supplied in-memory implementation is evidence only, not
authoritative persistence or complete `WorkflowEngine` conformance.

A bounded v0 invocation candidate now validates an exact live worker against the
retained manifest, invokes the SDK firer, canonically admits its closed result,
and revalidates the source observations and predecessor afterward. Only a
current success is mapped to a candidate external CPN binding. This remains
followed by a bounded pure-firing candidate that asks the provenance-bound CPN
firer to validate the mapped output and compute a successor and audit. A bounded
in-memory atomic-commit candidate then retains a compact commit identity,
consumes the reservation, and advances the marking coordinate under the same
lock. A bounded CPN plan closes the supplied definition bytes and candidate
execution-profile identity, but not every semantic section required by the
complete execution plan. Durable evidence persistence, crash recovery, and
committed replay remain absent, so these components do not complete
`WorkflowEngine` conformance.
