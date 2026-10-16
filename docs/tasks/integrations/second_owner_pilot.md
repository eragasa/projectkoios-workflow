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
baseline. The provisional Task boundaries and evidence-authority limits are
recorded in the [two-owner inventory](task_workflow_owner_inventory.md).

## Coordination status

The owner reports that its active experiment refactor is heavily dirty and has
not authorized a clean immutable repository revision. No live source revision
may therefore be used as pilot evidence yet.

Read-only inspection is limited to retained run
`ksdft2effmass.campaign.periodic-reduction.periodic1d.single-band-fourier-reduction.v1.run-20261014T184707Z`
at the current dimension-last experiment path. Its evidence-package identity is
`sha256:6e8d5db988df97d4b8cf7843b3baceb16e2eb70d2b03c729497a82251fca6377`.
The package was produced from a dirty worktree, so its recorded Git head is not
a clean source pin. A possible family-first layout remains a pending owner
direction and must not be described as present authority.

The content-addressed package supports provisional boundary inventory only. It
does not open the implementation, parity, or adoption gates below. Any future
fixture exercise must occur outside the immutable retained-run directory.

## Entry gates

- [x] Confirm the standalone Workflow SDK alpha is installable and consumed by
  Workflow and Simulations.
- [x] Confirm the bounded Simulations durable pure-action slice passes.
- [x] Make durable CPN commit the canonical experimental write direction.
- [ ] Coordinate with the active `ksdft2effmass` experiment refactor and pin a
  clean immutable source revision.
- [ ] Confirm the retained experiment version and fixtures can be exercised
  without external calculator execution or a scientific-validation claim.
- [x] Identify provisional Task boundaries using reuse, replay, evidence,
  authority, failure-isolation, or fan-out/fan-in needs; revalidate them against
  the future owner-authorized source revision before implementation.
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
  owner-declared numerical parity evidence within the declared tolerances.
  Demonstrate exact payload-digest equality separately; do not infer it from
  tolerance-bounded numerical parity.
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
