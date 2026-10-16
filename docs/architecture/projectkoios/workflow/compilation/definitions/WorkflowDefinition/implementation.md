# `WorkflowDefinition` implementation

## Responsibility

Construct through the final Workflow source-definition path or strict canonical
deserialization. Validate exact Task-instance order, unique identities,
composition connections, input/export contracts, and content identity.

Reject arbitrary subclasses, live Task or provider objects, direct self-targets,
and indirect child-definition cycles. A child Workflow reference carries exact
identity and contract closure only; its graph remains separately compiled.

Tests prove byte-stable canonicalization, owner mutation independence, version
mismatch rejection, parent substitution through the Task-definition root,
parent/child identity separation, and inability to embed runtime adapters or
callables.
