# `WorkflowExecutionPlan` implementation

## Responsibility

Use one frozen slotted aggregate with bounded tuples and canonical serialization. Validate that every transition requiring an external output has exactly one action mapping and that every nested route has exactly one non-self target.

DEFECT00003 conformance must demonstrate that changing any original Workflow, Task, adapter, or provider object after plan construction cannot change the plan, its serialized bytes, or its identity.
