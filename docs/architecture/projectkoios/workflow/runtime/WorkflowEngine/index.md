# `WorkflowEngine`

> **Status: provisional architecture iteration 2.** One durable pure atomic Task
> route is implemented experimentally. Effectful and workflow-backed Task routes
> remain architecture candidates.

## Responsibility

`WorkflowEngine` coordinates one compiled and linked Workflow plan against an
exact Workflow run. It selects one run-scoped Task instance through the
correlated CPN binding and dispatches exactly one compatible execution route:

- pure atomic Task through the SDK `Firer` boundary;
- effectful atomic Task through an accepted lifecycle handler; or
- workflow-backed Task through a distinct child Workflow run.

The engine does not confuse Task with transition, action, event, handler, or
provider. It derives and retains separate Task invocation, occurrence, attempt,
and run identities. A workflow-backed Task does not inline its child graph or
reuse the parent run; only an admitted terminal child delivery can become its
parent-visible result.

For a pure atomic Task, external-output admission is a Workflow runtime phase.
The engine obtains the plan-selected mapping, validates the exact SDK result and
deployment binding, revalidates authoritative sources, reservation, predecessor,
and selected CPN binding, and only then calls
`ColoredPetriNetTransitionFirer`.

For the QE saved-state candidate, the admitted CPN string is the opaque
Simulations-owned `artifact_set_identity`. Canonical artifact-set bytes and their
payload SHA-256 remain owner evidence and are never substituted for that logical
identity. The same generic Task model must preserve VASP as a different owner
specialization without assuming QE saved-state semantics.

The engine performs no discovery, plan inference, owner-domain import, provider
selection, or scientific interpretation. Rejected, failed, ambiguous, stale,
cancelled, or unadmitted child outcomes preserve evidence without fabricating a
Task result or CPN firing.

## Implemented bounded route

The existing experimental chain closes one pure atomic Task over exact plan and
binding identities, selected-binding evidence, repository-authorized inputs,
predecessor coordinates, occurrence, and attempt. It validates a live worker,
invokes the SDK firer, admits and maps only a current success, invokes the pure
CPN firer, and commits compact state, CPN replay evidence, lifecycle transition,
reservation consumption, and marking advancement in one SQLite transaction.

Compact replay, exact CPN refiring, lifecycle replay, and bounded safety-state
reconstruction invoke no owner. The compact-only writer remains compatibility
behavior. These components do not implement the complete Task/Workflow model,
effect lifecycle, child-run orchestration, global scheduler, or full
CPN-bindings conformance.
