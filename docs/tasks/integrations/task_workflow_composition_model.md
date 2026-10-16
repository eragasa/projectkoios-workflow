# Task and Workflow composition model

## Objective

Define the common composition language needed to break owner monoliths into
cohesive durable units without moving owner semantics into Workflow. A parent
Workflow sees only Tasks. A Workflow is itself a composite Task and therefore
may be invoked by a parent while retaining a distinct child Workflow run.

This task selects terminology and semantic boundaries before selecting a final
Python API. It does not add `Task` or `Workflow` to the released SDK alpha.

## Owner evidence

Simulations already demonstrates provider-specific implementations of one
calculator-neutral Task role:

- `PwDftScfHandlerTask` retains shared SCF task correlation;
- `QePwDftScfTask` and `VaspPwDftScfTask` retain different backend resources;
- `QePwDftScfActionHandler` and `VaspPwDftScfActionHandler` execute the common
  SCF action/event lifecycle; and
- `LocalPwDftScfWorkflow` keeps the lifecycle topology calculator-neutral.

`ksdft2effmass` supplies complementary composition evidence. Its maintained
`experiments/` tree contains typed deterministic experiment Actions, composite
scientific workflows, refinement/family execution shapes, and immutable
Definition-to-Result boundaries. Its retained single-band Fourier-reduction
experiment is the preferred independent pure owner fixture after a clean source
revision is pinned.

## Required semantic model

- [ ] Define `Task` as the parent-visible unit of work.
- [ ] Define `Workflow` as a composite specialization of `Task`.
- [ ] Require a Workflow composition to contain Task instances; do not create a
  second parent-facing collection named child workflows.
- [ ] When a Task is backed by a Workflow, create and retain a distinct child
  Workflow run rather than executing the child graph inside the parent run.
- [ ] Distinguish reusable Task definition, run-scoped Task instance, Task
  invocation, occurrence, attempt, and result identities.
- [ ] Distinguish Tasks from owner actions, events, CPN transitions, lifecycle
  commands, providers, handlers, and evidence records.
- [ ] Keep every executable net instance flat. Workflow-backed Tasks correlate a
  separately compiled child plan; they do not embed its CPN graph into the
  parent definition.
- [ ] Reject direct and indirect self-nesting in the retained definition closure.

## Definition and execution separation

- [ ] Represent Task definitions and instances as immutable bounded values.
- [ ] Keep execution behavior in a nominal handler, firer, or child-run service;
  a retained Task definition contains no callable, executable, path, credential,
  repository, worker object, or provider object.
- [ ] Permit owner-controlled Task specializations such as QE and VASP without
  moving backend fields into the generic SDK.
- [ ] Treat the existing SDK `Firer` as the validated owner boundary for one
  pure atomic Task.
- [ ] Encapsulate the current durable pure-action services as the execution
  strategy for a pure Task only after the common Task contract is accepted.
- [ ] Keep effectful Task execution behind the separate effectful-integration
  gate.
- [ ] Retain owner payload bodies, arrays, matrices, spectra, native artifacts,
  private locators, and backend configuration outside compact Workflow state.

## Task-boundary test

Promote an owner operation to a Task only when at least one of these properties
is required:

- independent reuse or substitution;
- independent durable identity or evidence;
- isolated failure, retry, or authority scope;
- replay, cache, or restart from an admitted result;
- fan-out, fan-in, or independent scheduling; or
- a separately testable owner contract.

Private numerical helpers and implementation-only transformations remain normal
methods or owner Actions. Parameterization alone does not create a Task.

## Required owner evidence

- [ ] Inventory the common Simulations SCF lifecycle and exact QE/VASP Task
  variation points without changing the owner implementation.
- [ ] Prove that a generic Task model does not flatten QE and VASP resources into
  one universal provider record.
- [ ] Pin one clean retained `ksdft2effmass/experiments/` revision.
- [ ] Identify cohesive Task boundaries in the retained single-band experiment.
- [ ] Preserve its typed Definition-to-Result API while adapting execution.
- [ ] Demonstrate one atomic pure Task and one workflow-backed Task.
- [ ] Demonstrate parent/child identity separation and owner-independent replay.
- [ ] Record every SDK, plan, binding, runtime, and persistence change required
  by the two owner shapes.

## API gate

Only after the evidence above is reviewed may Workflow accept exact nominal SDK
ABCs. The expected direction is a nominal `Task` source contract and a nominal
`Workflow(Task)` composite contract with validated non-overridable definition
construction. Exact names, fields, generic parameters, and compatibility rules
remain open until that gate.

## Exclusions

This task does not authorize calculator execution, effect migration, removal of
SNAKES, changes to the active `ksdft2effmass` experiment refactor, direct owner
inheritance from an unreleased SDK, or conversion of every experiment stage into
a durable Task.
