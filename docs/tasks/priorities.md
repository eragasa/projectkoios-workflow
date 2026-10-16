# Workflow task priorities

## Current direction

The QE saved-state pilot demonstrates concrete value for authoritative source
admission, atomic durable pure execution, and owner-independent replay. The
Simulations and `ksdft2effmass` evidence also shows that the long-term reusable
unit is a Task, not an isolated provider call:

- a parent Workflow contains Task instances;
- a Workflow is itself a composite Task when invoked by a parent;
- a workflow-backed Task receives a distinct child Workflow run;
- owner repositories retain their typed actions, events, results, codecs, and
  provider-specific Task records; and
- handlers, firers, and child-run services execute Tasks without becoming
  durable Task definitions.

The current investment rule is therefore:

> Preserve owner-facing Task and Workflow contracts. Build a common composition
> model from real owner evidence, and apply Workflow's durable pure execution
> machinery only to Tasks whose semantics are effect-free.

The existing Simulations `PwDftScfWorkflowFacade`, typed actions/events, local
SNAKES implementation, and QE/VASP Task split remain authoritative owner
architecture. Workflow's QE artifact-set path is a bounded pure Task candidate,
not a replacement for calculator registration, submission, or reconciliation.

## Completed enabling evidence

- The durable CPN commit service is the canonical experimental write direction.
- Compact-only writing is compatibility behavior with no production execution
  callers.
- The QE source adapter and durable vertical slice prove one real owner path.
- Compact replay, CPN refiring, lifecycle replay, and bounded safety-state
  reconstruction do not reinvoke the owner.

Existing `pure-action` names remain compatibility and evidence names. A future
accepted surface may use `pure Task execution`; no rename occurs without an
explicit compatibility migration.

## Now — establish the composition model

1. Complete the
   [Task and Workflow composition model](integrations/task_workflow_composition_model.md).
2. Review the completed
   [two-owner Task and Workflow inventory](integrations/task_workflow_owner_inventory.md),
   including Simulations' calculator-neutral SCF topology, common task
   correlation, QE/VASP Task specializations, and matching handlers.
3. Preserve the
   [selective Simulations adoption boundary](integrations/simulations/selective_runtime_adoption.md)
   while documenting that the SCF Workflow contains backend-specialized Task
   work and may later be exposed as a Task to a parent.
4. Pin an owner-supplied and authorized clean immutable revision of the retained
   `ksdft2effmass/experiments/periodic-reduction/single-band-fourier-reduction/periodic1d`
   experiment after the active refactor yields one. Coordination found an exact
   content-addressed retained package for provisional inventory, but the owner
   reports no clean repository revision that may yet be pinned.
5. Keep the completed
   [canonical durable pure-action path](integrations/canonical_durable_pure_action_path.md)
   unchanged as enabling evidence.

Do not add another replay variant, persistence layer, or internal orchestration
record unless the composition work exposes a concrete missing safety property.

## Next — validate the model through two owners

1. Run the revised [second owner SDK pilot](integrations/second_owner_pilot.md)
   against the retained `ksdft2effmass` experiment.
2. Preserve its typed Definition-to-Result API while extracting only cohesive
   Task boundaries justified by reuse, replay, evidence, authority, failure
   isolation, or fan-out/fan-in.
3. Demonstrate one atomic pure Task and one workflow-backed Task with distinct
   parent and child run identities.
4. Compare the experiment shape with Simulations' QE/VASP provider
   specialization before accepting exact nominal SDK `Task` and
   `Workflow(Task)` ABCs.
5. If both shapes succeed, encapsulate the durable pure-action runtime as the
   supported pure Task execution strategy and close only the minimum
   plan/profile, packaging, compatibility, source-authority, and worker-isolation
   gaps required by those owners.
6. Then activate the
   [experimental surface retirement](tech_debt/retire_experimental_action_surface.md)
   and [broader adoption gate](integrations/broader_adoption_gate.md).

## Later — separately gated capabilities

- Effect dispatch, reconciliation, cancellation, retries, and ambiguous outcomes
  remain behind the [effectful integration gate](integrations/effectful_integration_gate.md).
- A Workflow-backed implementation of the Simulations SCF facade may be
  evaluated only after that gate passes and only through owner-controlled
  behavioral-equivalence tests covering both QE and VASP Task routes.
- Direct owner inheritance from accepted SDK Task/Workflow ABCs may replace an
  adapter only after compatibility evidence proves that it preserves the owner
  API and dependency direction.
- Global multi-occurrence scheduler replay and complete CPN-bindings replay are
  deferred until a real owner requires them.

## Explicitly not prioritized

- flattening QE and VASP into a universal provider Task record;
- treating a complete owner Workflow as one permanently opaque atomic firing;
- replacing Simulations' current SCF facade or local SNAKES lifecycle;
- making protected owner code import Workflow service, persistence, compiler, or
  CPN runtime implementations;
- effectful execution through the pure `Firer` boundary;
- converting every numerical helper into a Task;
- changing the active `ksdft2effmass` experiment refactor without owner
  coordination;
- infrastructure growth justified only by internal architectural completeness;
  or
- claiming full CPN-bindings conformance from bounded experimental records.

## Revisit conditions

Revisit the ordering only when at least one of the following occurs:

- the two owner shapes cannot share a Task/Workflow contract without a concrete
  semantic conflict;
- a production pure Task requires guarantees absent from the durable QE path;
- an owner requests durable effect lifecycle behavior and the effectful gate has
  accepted semantics; or
- operating evidence shows that an existing owner architecture cannot satisfy a
  required durability, concurrency, or replay property.
