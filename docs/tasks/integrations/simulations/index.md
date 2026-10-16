# Simulations integration tasks

This directory indexes bounded integration work between
`projectkoios-workflow` and `projectkoios-simulations`.

Until an accepted Workflow release exists, base owner integrations remain
limited to the standalone pinned SDK. Full-runtime adapters stay in outward
namespaces behind an explicit optional dependency and are not compatibility
promises for protected simulation core or reusable workflow contracts.

## Iteration-2 owner evidence

Simulations already demonstrates one calculator-neutral Workflow coordinating a
provider-specialized Task role:

- `PwDftScfHandlerTask` retains common correlation;
- `QePwDftScfTask` and `VaspPwDftScfTask` retain backend-specific resources;
- matching handlers execute common SCF actions and emit common events; and
- `LocalPwDftScfWorkflow` retains the backend-neutral SNAKES lifecycle.

Workflow integration must preserve that split. A parent may later see the SCF
Workflow as one Task and create a distinct SCF child run, but the child must
retain its internal calculator Task and must not flatten QE and VASP into a
generic provider record.

## Tasks

- [Selective Workflow runtime adoption](selective_runtime_adoption.md) — owner
  boundary, QE/VASP Task evidence, and future composition/migration gate.
- [QE artifact-set Workflow SDK pilot](qe_artifact_set_sdk_pilot.md) — first
  pure consumer fixture and isolated owner-side SDK firing evidence.
- [QE artifact-set durable vertical-slice evidence](qe_artifact_set_durable_vertical_slice_evidence.md)
  — source authorization, invocation, pure CPN firing, atomic commit, and replay.

The remaining common composition work is tracked by the
[Task and Workflow composition model](../task_workflow_composition_model.md).
Full-plan, release, and isolation gaps remain in the
[pure-firing foundations](../pure_firing_foundations.md) and
[pure-firing vertical slice](../pure_firing_vertical_slice.md).
