# Second owner SDK pilot

## Objective

Use one retained `ksdft2effmass` numerical experiment to test whether Workflow's
pure execution boundary and the proposed Task/Workflow composition model are
genuinely generic rather than shaped around Simulations artifacts.

The pilot must contribute to the ongoing experiment-monolith decomposition
without forcing Workflow transport, persistence, or CPN types into numerical
source code. It follows the
[Task and Workflow composition model](task_workflow_composition_model.md) and
precedes additional speculative runtime infrastructure.

## Selected owner direction

The preferred initial fixture is:

`ksdft2effmass/experiments/periodic-reduction/single-band-fourier-reduction/periodic1d`

It is preferred over the earlier Ingestion or References candidates because it
is structurally independent of the QE artifact-set projector, has an immutable
retained experiment version and evidence, exposes a typed
Definition-to-Result operation, and composes reusable scientific Actions. The
actively changing model-adequacy experiments may later supply refinement,
fan-out, and fan-in evidence, but they are not the initial compatibility
baseline.

## Entry gates

- [x] Confirm the standalone Workflow SDK alpha is installable and consumed by
  Workflow and Simulations.
- [x] Confirm the bounded Simulations durable pure-action slice passes.
- [x] Make durable CPN commit the canonical experimental write direction.
- [ ] Coordinate with the active `ksdft2effmass` experiment refactor and pin a
  clean immutable source revision.
- [ ] Confirm the retained experiment version and fixtures can be exercised
  without external calculator execution or a scientific-validation claim.
- [ ] Identify proposed Task boundaries using reuse, replay, evidence, authority,
  failure-isolation, or fan-out/fan-in needs.
- [ ] Confirm no proposed mapping requires reusable experiment code to import
  Workflow service, compiler, persistence, or CPN runtime implementations.

## Required evidence

- [ ] Preserve the owner experiment's typed Definition-to-Result API.
- [ ] Implement an owner-owned nominal integration ABC encapsulating the SDK
  `Firer` boundary.
- [ ] Implement pure owner codecs for exact canonical request, result, and
  evidence bytes.
- [ ] Keep arrays, matrices, spectra, owner payload bodies, and private locators
  outside compact Workflow state.
- [ ] First demonstrate isolated owner-side request/result invocation.
- [ ] Demonstrate one cohesive atomic pure Task without treating every numerical
  helper as a Task.
- [ ] Demonstrate one workflow-backed Task or multi-Task composition with
  distinct parent Task invocation and child Workflow-run identities.
- [ ] Compare direct owner execution with Workflow-backed execution and retain
  exact deterministic parity evidence within the owner's declared tolerances.
- [ ] Retain negative correlation, bound, malformed-payload, stale-source, and
  replay tests.
- [ ] Record every SDK, plan, binding, runtime, and persistence change required
  by the owner.

## Generality questions

The pilot must answer:

- Can an owner keep typed numerical definitions and results internally while
  using canonical bytes only at the SDK boundary?
- Can durable Task boundaries reduce a monolithic experiment without exporting
  private implementation helpers?
- Can a Workflow be invoked as a Task while the parent and child retain separate
  runs and replay evidence?
- Can the same generic model preserve Simulations' provider-specialized QE/VASP
  Tasks without adding scientific or backend fields to the SDK?

A required owner-specific field in the generic SDK triggers architecture review
rather than automatic expansion. Failure to find natural Task boundaries is
evidence against decomposition through Workflow, not a reason to manufacture
fine-grained Tasks.

## Exclusions

This pilot authorizes no external scientific calculation, dependency change,
scientific claim, publication action, mutation of active uncommitted experiment
work, effect lifecycle, direct runtime import into reusable owner libraries, or
broader SDK adoption.
