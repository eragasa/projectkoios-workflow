# `projectkoios.workflow` implementation

> **Status: provisional architecture iteration 2.** This file describes target
> boundaries and evidence gates; it is not an implementation or migration
> authorization.

## Responsibility

The implementation separates a standard-library SDK surface from service
internals. The SDK owns frozen records, nominal ABCs, and validating template
methods. Service internals own compilation, the CPN kernel, deployment linking,
runtime coordination, persistence, scheduling, and transports.

The central iteration-2 distinction is between Task definition and Task
execution:

- a Task definition is immutable parent-visible declarative state;
- a Task instance is one run-scoped member of a Workflow composition;
- a pure atomic Task is executed through an SDK `Firer`;
- an effectful atomic Task is executed through an accepted lifecycle handler;
- a Workflow is a composite Task whose invocation creates a distinct child run;
  and
- actions, events, lifecycle commands, CPN transitions, handlers, and providers
  remain separate types.

The target source boundary uses nominal runtime-enforced interfaces. The exact
future API remains gated on two owner shapes; it is not added retroactively to
SDK `0.1.0a1`. A validating `Workflow(Task)` source base should construct a
closed immutable definition through non-overridable template behavior, but it
must not execute Tasks, inspect markings, discover providers, or own a run.

## Owner evidence

Simulations demonstrates provider specialization without workflow-topology
duplication: `PwDftScfHandlerTask` retains common correlation,
`QePwDftScfTask` and `VaspPwDftScfTask` retain backend-specific resources, and
separate handlers produce common SCF events for one calculator-neutral
lifecycle. The generic architecture must preserve that split without storing
paths, executables, pseudopotentials, execution requests, or live handlers in a
plan.

`ksdft2effmass/experiments/` demonstrates typed deterministic numerical Actions,
composite workflows, refinement families, and potential fan-out/fan-in. The
retained single-band Fourier-reduction experiment is the preferred independent
pure owner fixture after a clean revision is pinned. Task extraction is
justified only by reuse, durable evidence, replay, authority, failure isolation,
or scheduling. Private numerical helpers remain ordinary owner implementation.

## Compilation and execution boundaries

Each Workflow compiles to one flat canonical CPN plan. A workflow-backed Task
retains an exact child definition/plan reference and route contract; it does not
inline the child graph. Runtime creates the child run, correlates it with the
parent Task invocation, and delivers only an admitted terminal export to the
parent transition. Parent and child commits remain separate.

Plans and deployment bindings retain only bounded immutable descriptors and
identities. Live owner objects and implementations stay in isolated owner or
worker processes. Compact Workflow state retains identities and admitted
evidence references, never owner payload bodies or private locators.

The implemented `ExperimentalWorkflowPureAction*` chain is the candidate pure
atomic Task executor. Its names, identities, schemas, canonical bytes, and
rejection behavior remain unchanged until a separately accepted compatibility
migration introduces supported pure-Task terminology.

## Modular-monolith direction

Iteration 2 first targets a modular monolith. Cohesive Task contracts, immutable
inputs/results, explicit composition, and independent tests are required before
any process or service split. Distribution is justified later by operational
needs; it is not inferred from Task membership.

An owner operation becomes a Task only when it needs at least one independent
reuse, durable identity/evidence, retry or authority scope, replay/cache/restart,
fan-out/fan-in, or separately testable contract. Parameterization and method
size alone are insufficient.

## Common evidence gates

- Immutable plan independence from live owners and providers.
- Exact separation of Task definition, Task instance, invocation, occurrence,
  attempt, result, handler, and Workflow run.
- Parent/child identity correlation without topology or history flattening.
- Provider-specialized Task parity without generic provider-field growth.
- Exact CPN enablement, selection, reservation, output admission, and firing.
- Crash, ambiguity, reconciliation, cancellation, and restart evidence before
  any effectful Task migration.
- Same-store replay and independent rebuild without owner effect re-execution.
- Owner payload and private-data exclusion from compact state.
- Cross-owner conformance before accepting SDK Task/Workflow APIs.
- Migration equivalence before retiring any façade, SNAKES runtime, script, or
  historical engine.

## Issue register

Stable Workflow-local questions and external dependency gates remain in the
[provisional issue register](issues/). Cross-repository product decisions and
owner defects remain authoritative in their owning repositories.
