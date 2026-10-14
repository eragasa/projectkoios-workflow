# Workflow tasks

This directory indexes bounded implementation and review tasks owned by
`projectkoios-workflow`.

Task documents record scope and evidence; they do not by themselves accept a
contract, authorize a cross-repository migration, or replace authoritative
GitHub issue and decision records.

## Categories

- [Integration tasks](integrations/) — SDK readiness, pure consumer pilots,
  broader adoption, and effectful-integration gates.
- [Technical-debt tasks](tech_debt/) — removal of private duplicates after an
  accepted SDK surface exists.

## Recommended sequence

1. Establish SDK alpha consumption readiness.
2. Complete the Simulations-backed pure firing vertical slice.
3. Validate the boundary with a structurally different second owner.
4. Pass the broader adoption gate.
5. Integrate effects only after the separate effectful-integration gate passes.
