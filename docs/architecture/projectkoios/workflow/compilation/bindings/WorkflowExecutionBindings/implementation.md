# `WorkflowExecutionBindings` implementation

## Responsibility

Represent deployment bindings as frozen descriptors and opaque service handles
with canonical serialization. Keep process-local resolved implementations in a
separate worker-only table keyed by retained binding identity.

A pure action binding must retain the exact action descriptor and
result-mapping descriptor identities already named by the execution plan. The
linker verifies exact agreement and cannot select another semantic mapping for
the same plan. The mapping descriptor records ordered output and evidence roles,
expected schema/codec/representation metadata, the target CPN external-variable
identity and value kind, and its own versioned content identity. It contains no
owner payload bytes, Python classes, live codecs, or callables.

For the QE SCF artifact-set direction, linking must require one canonical
`artifact_set_identity` scalar output compatible with a declared `STRING`
external variable and one bounded canonical `artifact_set` evidence document.
The linker rejects a mapping that substitutes the evidence payload SHA-256 for
the owner logical identity.

Validation must reject stale provider capability digests, unsupported protocol
versions, reordered bindings, a mapping identity different from the execution
plan, output-role or variable mismatch, incompatible value kinds, missing
evidence metadata, route mismatch, missing reconciliation guarantees, and
nested-child disagreement. Provider unavailability is runtime status, not
removal from this artifact.
