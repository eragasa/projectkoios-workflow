# `WorkflowExecutionPlan` implementation

## Responsibility

Use one frozen slotted aggregate with bounded tuples and canonical
serialization. Validate that every transition requiring an external output has
exactly one action mapping and that every nested route has exactly one non-self
target.

The current `ExperimentalWorkflowPureActionExecutionPlan` is a frozen, slotted,
content-identified subset. It reconstructs the output-mapping descriptor,
retains the exact nominal selected-binding profile, and derives its identity
from those two semantic identities. Record construction does not consult the
current encoder default, so an older retained profile remains representable
after a newer implementation is installed. Compiler and runtime support checks
belong to separate validation boundaries. The record stores no live firer,
worker, codec, provider, or repository object. Canonical serialization and
complete plan closure remain unimplemented and must not be inferred from this
subset.

`ExperimentalWorkflowPureActionInputPlan` extends that unchanged base-plan
identity with an ordered, content-identified input-source mapping for every SDK
input role. It rejects missing, duplicate, reordered, or contract-incompatible
roles. Behavior-affecting source kind, source profile, or mapping-version
changes produce a different input-plan identity. The wrapper preserves
reconstruction of plans retained before input mapping was introduced. It
remains an experimental subset rather than the canonical complete plan.

DEFECT00003 conformance must demonstrate that changing any original Workflow,
Task, adapter, or provider object after plan construction cannot change the
complete plan, its serialized bytes, or its identity.
