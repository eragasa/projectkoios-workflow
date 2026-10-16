# Workflow architecture iteration 2

## Responsibility

This record marks the second architecture iteration of
`projectkoios-workflow`. It is an architecture revision marker, not a package
version, release candidate, compatibility promise, migration authorization, or
release tag.

## Iteration 1 evidence

The first iteration established a standalone pure-firing SDK boundary and one
real-owner durable vertical slice. It proved exact selected-binding request
construction, authoritative source resolution, owner invocation, opaque result
admission, pure CPN firing, atomic durable commit, and bounded owner-independent
replay. Its implementation and evidence continue to use the term `pure action`.

That iteration did not establish a reusable parent/child composition model, a
supported Task abstraction, effectful execution, complete plan/profile closure,
or broad owner adoption.

## Iteration 2 direction

The second iteration treats Task as the parent-visible unit of work and Workflow
as a composite Task. A parent contains Task instances only. When one Task is
backed by a Workflow, runtime creates a distinct child Workflow run correlated
to the parent Task invocation; it does not embed the child CPN in the parent
run.

Owner evidence shapes this direction:

- Simulations keeps one calculator-neutral SCF lifecycle while
  `QePwDftScfTask` and `VaspPwDftScfTask` specialize the common
  `PwDftScfHandlerTask` correlation and use separate handlers.
- `ksdft2effmass/experiments/` contains typed deterministic experiments,
  composite numerical workflows, and refinement shapes that can test cohesive
  pure Task boundaries and monolith decomposition.

Execution is separate from retained Task definition. A pure atomic Task uses the
validated SDK `Firer` boundary and the existing durable pure-action runtime. An
effectful Task uses a separately accepted lifecycle handler. A workflow-backed
Task creates and reconciles a child run. Actions, events, lifecycle commands,
and CPN transitions are not reclassified as Tasks merely because they occur
inside a Workflow.

## Compatibility direction

Existing `0.1.0a1` SDK records, canonical bytes, identity domains, and
`ExperimentalWorkflowPureAction*` evidence remain unchanged until an explicit
compatibility migration is accepted. Iteration 2 architecture may use the term
`pure Task execution` for the successor abstraction, but it does not rename
implemented APIs or claim that `Task` and `Workflow` are already public SDK
classes.

Owner adoption begins through adapters. Direct inheritance from future nominal
SDK ABCs is considered only after Simulations and one structurally independent
experiment owner demonstrate compatible semantics and dependency direction.
