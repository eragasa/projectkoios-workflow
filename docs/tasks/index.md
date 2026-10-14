# Workflow tasks

This directory indexes bounded implementation and review tasks owned by
`projectkoios-workflow`.

Task documents record scope and evidence; they do not by themselves accept a
contract, authorize a cross-repository migration, or replace authoritative
GitHub issue and decision records.

## Categories

- [Integration tasks](integrations/) — SDK readiness, pure consumer pilots,
  authoritative pure-firing foundations, broader adoption, and
  effectful-integration gates.
- [Technical-debt tasks](tech_debt/) — bounded contract-ownership, validation,
  and experimental-surface cleanup after their activation conditions hold.

## Recommended sequence

1. Establish SDK alpha consumption readiness.
2. Complete the Simulations owner-side SDK pilot.
3. Establish the authoritative pure-firing foundations.
4. Complete the Simulations-backed pure-firing vertical slice.
5. Validate the boundary with a structurally different second owner.
6. Pass the broader adoption gate.
7. Integrate effects only after the separate effectful-integration gate passes.
