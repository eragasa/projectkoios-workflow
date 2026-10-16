# `WorkflowExecutionPlan` implementation

## Responsibility

Use one frozen slotted aggregate with bounded tuples and canonical serialization.
Validate that every Task instance has exactly one compatible compiled mapping.
Atomic Tasks bind one pure or effectful route. Workflow-backed Tasks bind one
non-self separately compiled child plan, exact input/export contracts, and one
terminal-delivery mapping.

The plan contains the current Workflow's flat CPN only. Child definition and plan
identities are closed references; child markings, histories, provider objects,
and graph bodies are not copied into the parent plan. Direct and indirect plan
cycles are rejected.

Current `ExperimentalWorkflowPureActionExecutionPlan`, input plan, and CPN plan
remain frozen content-identified subsets for one pure atomic route. Their
identity derivations, canonical representations, reconstruction of older
profiles, and rejection behavior must not change as a side effect of iteration
2. A later accepted plan may embed or translate those semantics only through an
explicit compatibility decision.

Complete conformance must prove that changing any original owner Workflow, Task,
adapter, handler, or provider after construction cannot change the plan, its
serialized bytes, or its identity.
