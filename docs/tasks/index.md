# Workflow tasks

This directory indexes bounded implementation and review tasks owned by
`projectkoios-workflow`. Task documents record scope and evidence; they do not
accept contracts, authorize cross-repository migration, or replace authoritative
owner decisions.

## Current priorities

See [Workflow task priorities](priorities.md). Architecture iteration 2 treats a
Task as the parent-visible unit and a Workflow as a composite Task. Existing
`pure-action` implementation names remain compatibility evidence while the
common Task/Workflow model is validated against Simulations and
`ksdft2effmass/experiments/`.

## Categories

- [Integration tasks](integrations/) — Task/Workflow composition, SDK readiness,
  owner pilots, pure execution foundations, broader adoption, and effect gates.
- [Technical-debt tasks](tech_debt/) — bounded contract ownership, validation,
  and experimental-surface cleanup after their activation conditions hold.

## Recommended sequence

1. Complete the
   [Task and Workflow composition model](integrations/task_workflow_composition_model.md).
2. Preserve and document Simulations' calculator-neutral SCF Workflow plus
   QE/VASP Task specialization.
3. Validate independent pure composition with the retained
   `ksdft2effmass` experiment pilot.
4. Accept exact nominal SDK Task/Workflow contracts only after the two owner
   shapes agree.
5. Encapsulate the canonical durable pure-action path as pure Task execution
   without changing retained identities or bytes.
6. Close only the packaging, plan/profile, authority, and worker-isolation gaps
   required by those owners.
7. Retire or internalize experimental surfaces before broader adoption.
8. Integrate effects only after the separate effectful-integration gate passes.
9. Consider owner lifecycle migration only after effect semantics, provider
   parity, and behavioral equivalence are proven.
