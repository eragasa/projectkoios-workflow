# `WorkflowExecutionPlanConstructor` implementation

## Responsibility

Expose construction as a typed pure operation. Preserve definition-owned Task,
port, variable, and composition order; canonicalize only where the contract
explicitly declares order irrelevant.

Validate exact Task-definition membership, atomic route compatibility,
workflow-backed child target and input/export closure, direct and indirect cycle
absence, fragment composition, and canonical flat parent CPN output. Reject
implicit connections inferred from names, schemas, annotations, registry
proximity, or provider availability.

Tests cover missing, extra, reordered, duplicate, or wrong-kind Tasks; unresolved
connections; priority ambiguity; child self/cycles; absent or extra child
contracts; nondeterministic composition; action/lowering mismatch; invalid CPN
output; and live-object exclusion.
