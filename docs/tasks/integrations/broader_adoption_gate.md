# Broader SDK adoption gate

## Objective

Define the evidence required before Workflow recommends iteration-2 Task,
Workflow, or pure execution contracts to additional owner repositories.

## Composition gate

- [ ] Accept the
  [Task and Workflow composition model](task_workflow_composition_model.md).
- [ ] Distinguish Task definition, run-scoped Task instance, invocation,
  occurrence, attempt, result, handler/firer, Workflow definition, and Workflow
  run.
- [ ] Require parent compositions to contain Tasks and Workflow-backed Tasks to
  create distinct child runs.
- [ ] Prove parent and child plans, markings, histories, and identities remain
  separate.
- [ ] Reject direct and indirect Workflow-definition cycles.
- [ ] Prove actions, events, lifecycle commands, and CPN transitions cannot be
  substituted for Task identity.

## Owner-evidence gate

- [ ] Confirm two structurally independent owner fixtures pass.
- [ ] Use Simulations to demonstrate one calculator-neutral Workflow with QE and
  VASP provider-specific Task records and handlers.
- [ ] Do not count QE and VASP as two independent owners; they are provider
  specialization evidence within Simulations.
- [ ] Use the retained `ksdft2effmass` experiment to demonstrate typed pure Task
  decomposition and workflow-backed composition.
- [ ] Preserve owner-facing typed APIs and prove no protected owner core imports
  Workflow service, persistence, compiler, or CPN runtime implementations.
- [ ] Prove retained plans contain immutable descriptors and identities rather
  than live owner Tasks, handlers, providers, child objects, or repositories.
- [ ] Prove Workflow state contains no backend configuration, private locator,
  numerical array, scientific payload body, or native artifact body.

## Runtime and compatibility gate

- [ ] Complete the required [pure-firing foundations](pure_firing_foundations.md)
  and [vertical-slice](pure_firing_vertical_slice.md) work.
- [ ] Accept SDK compatibility, versioning, deprecation, and schema-evolution
  rules.
- [ ] Validate immutable manifests and real isolated worker loading.
- [ ] Ensure supported owner paths expose no experimental Workflow service-side
  API.
- [ ] Retain every behavior profile required for deterministic replay.
- [ ] Demonstrate replay across every supported SDK and retained-schema version.
- [ ] Demonstrate that direct construction or nominal type membership cannot
  bypass runtime admission.
- [ ] Add automated tests for supported upgrades and explicit incompatibility.
- [ ] Document rollback and exact-version pinning behavior.
- [ ] Retain an explicit migration for any `pure-action` to `pure Task`
  terminology or API change.

## Outcome

Passing this gate permits separately authorized owner adoption work. It does not
migrate an owner workflow facade, accept effectful lifecycle semantics, authorize
calculator execution, release a package, create a tag, or deploy a service.
