# Integration tasks

This directory indexes work that integrates Workflow-owned contracts and runtime
behavior with external owner repositories. Integration tasks preserve owner
boundaries, identify exact contract versions, and distinguish fixture review
from runtime adoption.

## Architecture iteration 2 sequence

1. Establish the
   [Task and Workflow composition model](task_workflow_composition_model.md): a
   parent contains Tasks, a Workflow is a composite Task, and a workflow-backed
   Task creates a distinct child run.
2. Use the
   [two-owner Task and Workflow inventory](task_workflow_owner_inventory.md) to
   constrain the common model while preserving the
   [selective Simulations adoption boundary](simulations/selective_runtime_adoption.md).
3. Follow the lean
   [`ksdft2effmass` workflow capability migration](ksdft2effmass_workflow_capability_migration.md):
   deduplicate the already-identical CPN kernel first, retain owner science,
   archive only evidenced history readers, and deprecate legacy runtime
   overgrowth rather than porting it wholesale.
4. Use the revised [second owner SDK pilot](second_owner_pilot.md) to test pure
   Task decomposition and workflow-backed composition in the retained
   `ksdft2effmass` single-band experiment after its owner authorizes a clean
   immutable source revision.
5. Treat the completed
   [canonical durable pure-action path](canonical_durable_pure_action_path.md) as
   the implementation candidate for pure atomic Task execution. Preserve its
   current names and bytes until an explicit compatibility migration.
6. Close remaining [pure-firing foundations](pure_firing_foundations.md) only to
   the extent required by the two-owner Task model and a supported pure route.
7. Complete remaining
   [pure-firing vertical-slice](pure_firing_vertical_slice.md) release and
   worker-isolation gates.
8. Pass the [broader SDK adoption gate](broader_adoption_gate.md).
9. Address the [effectful integration gate](effectful_integration_gate.md) only
   when an owner requests durable effect orchestration.

## Existing evidence

Detailed bounded evidence remains indexed by the foundations task, including
selected-binding construction, source authority, reservation, owner invocation,
pure CPN firing, atomic persistence, compact replay, CPN refiring, lifecycle
replay, safety-state reconstruction, and the real QE vertical slice. The
[SDK reproducible artifact candidate](sdk_alpha_reproducible_artifact_candidate.md)
separately records non-releasing wheel, metadata, installation, and owner
compatibility evidence. Exact committed-source evidence now verifies the
license-package correction; two public-clone rebuilds and Workflow CI also
passed. The operator selected retaining `0.1.0a1`. Any release authorization
remains outstanding.

That evidence establishes one pure atomic route. It does not establish public
Task/Workflow SDK contracts, workflow-backed child runs, effect lifecycle,
global scheduler replay, or complete CPN-bindings conformance.
