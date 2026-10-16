# Workflow tasks

This directory indexes bounded implementation and review tasks owned by
`projectkoios-workflow`.

Task documents record scope and evidence; they do not by themselves accept a
contract, authorize a cross-repository migration, or replace authoritative
GitHub issue and decision records.

## Current priorities

See [Workflow task priorities](priorities.md). The current direction preserves
owner-facing domain workflow facades and applies Workflow selectively to durable
pure actions. Broader migration and effect support remain gated.

## Categories

- [Integration tasks](integrations/) — SDK readiness, pure consumer pilots,
  authoritative pure-firing foundations, broader adoption, and
  effectful-integration gates.
- [Technical-debt tasks](tech_debt/) — bounded contract-ownership, validation,
  and experimental-surface cleanup after their activation conditions hold.

## Recommended sequence

1. Preserve the
   [selective Simulations adoption boundary](integrations/simulations/selective_runtime_adoption.md).
2. Make the
   [durable CPN commit path canonical](integrations/canonical_durable_pure_action_path.md)
   without adding more infrastructure.
3. Validate SDK generality with a structurally different pure owner.
4. Close only the packaging, plan/profile, authority, and worker-isolation gaps
   required by those two owners.
5. Retire or internalize experimental surfaces before broader adoption.
6. Integrate effects only after the separate effectful-integration gate passes.
7. Consider an owner lifecycle backend migration only after effect semantics and
   behavioral equivalence are proven.
