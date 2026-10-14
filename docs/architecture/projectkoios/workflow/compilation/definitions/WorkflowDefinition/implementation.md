# `WorkflowDefinition` implementation

## Responsibility

Construct only through the final `AbstractWorkflow.definition` path or strict deserialization. Validate content identity on construction and deserialization. Reject arbitrary subclasses so a retained plan has one closed representation.

Tests must prove byte-stable canonicalization, owner mutation independence, version mismatch rejection, and inability to embed runtime adapters or callables.
