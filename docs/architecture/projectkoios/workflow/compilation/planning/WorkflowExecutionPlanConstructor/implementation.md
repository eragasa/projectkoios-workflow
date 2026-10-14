# `WorkflowExecutionPlanConstructor` implementation

## Responsibility

Expose the constructor as a typed action operation. Canonicalize caller order only where the definition declares order irrelevant; preserve definition-owned task and variable order everywhere else.

Validate explicit action-descriptor membership, request/result port compatibility, declared pure/effectful class, and required authority/idempotency/evidence colors. Reject descriptors that contradict their selected lowering. Do not infer or synthesize action connections from matching schemas, names, annotations, or registry proximity.

Tests cover missing/extra/reordered definitions, duplicate identities, unresolved or reflectively implied connections, priority ambiguity, nested self-targets, absent/extra nested targets, nondeterministic composition order, action/lowering mismatch, invalid CPN output, and live-object exclusion.
