# `projectkoios.workflow.sdk.registry` implementation

## Responsibility

Provide closed descriptor records, URI/version grammar, schema digests, supported protocol ranges, evidence versions, effect classes, authorization schemes, resource limits, and durable-start/reconciliation/cancellation guarantees.

A validating base may compute the canonical manifest digest and reject duplicates or contradictions. It must not inspect the persistent registry or infer runtime availability.
