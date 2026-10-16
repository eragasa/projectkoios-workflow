# `projectkoios.workflow` architecture

> **Status: provisional architecture iteration 2.** The implemented durable
> pure-action path remains prerelease evidence. The Task/Workflow composition
> model below is a candidate and authorizes no owner migration or release.

## Responsibility

`projectkoios.workflow` owns the generic CPN workflow platform: SDK contracts,
compilation, immutable definition and deployment artifacts, validation,
markings, enablement, deterministic selection, reservation, Task execution
coordination, pure firing, durable occurrences and attempts, provider
coordination, parent/child run correlation, replay, provenance, control-plane
services, and read-only visualization.

A Task is the parent-visible unit of work. A Workflow is a composite Task. A
Workflow composition contains Task instances; when one Task is backed by a
Workflow, runtime creates a distinct child Workflow run correlated to the parent
Task invocation. Every executable net instance remains flat, so child topology
is separately compiled rather than embedded in the parent CPN.

Task definition and Task execution are separate. Immutable definitions retain
identities, contracts, routes, and composition only. Pure atomic Tasks execute
through the SDK `Firer` boundary. Effectful Tasks require a separately accepted
lifecycle handler. Workflow-backed Tasks create and reconcile child runs.
Actions, events, lifecycle commands, providers, handlers, and CPN transitions
are not themselves Tasks merely by association.

Workflow does not own domain request semantics, scientific acceptance,
calculator formats, extraction correctness, owner payloads, provider-specific
resources, credentials, or publication decisions. Those remain with external
owners. Simulations' QE/VASP Task specialization and the typed experiments under
`ksdft2effmass/experiments/` are design evidence; they are not types to copy into
the generic SDK.

The current operator-selected candidate uses CPN as the sole executable process
formalism. Reusable behaviors such as fan-out, approval, timers, external
effects, retry, reconciliation, cancellation, and child delivery are fragment
templates compiled into flat validated nets—not parallel step or DAG runtimes.

## Architecture iteration

[Iteration 2](iteration-2.md) generalizes the first durable pure-action vertical
slice into a Task/Workflow composition model. Existing `pure-action` APIs and
evidence names remain unchanged until an explicit compatibility migration.
Architecture iteration 2 is not a package RC2 or compatibility promise.

## Open architecture questions

Exact SDK Task/Workflow class names and fields, physical distribution
boundaries, authority issuance, durable process supervision,
operational-companion-net composition, cancellation propagation, terminal child
delivery, storage technology, service-process separation, and worker dispatch
direction remain unresolved. The child documents present testable candidates
without closing those decisions.
