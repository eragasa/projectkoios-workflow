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

The current `ExperimentalWorkflowPureActionExecutionBindings` performs a strict
canonical SDK manifest round trip, reconstructs the experimental plan candidate,
and requires exactly one manifest descriptor equal to the plan-selected firer
descriptor. Its identity closes the exact candidate-plan and manifest
identities. It does not resolve or retain a live `Firer`.

`ExperimentalWorkflowPureActionInputBindings` links one exact input-extended
plan to those existing deployment bindings and rejects a substituted base plan.
The deployment cannot replace plan-selected source kinds, profiles, role order,
or mapping versions during input admission. The record retains no source
payload, repository, codec implementation, or callable.

Complete validation must additionally reject stale provider capability digests,
unsupported protocol versions, reordered bindings, a mapping identity different
from the execution plan, output-role or variable mismatch, incompatible value
kinds, missing evidence metadata, route mismatch, missing reconciliation
guarantees, and nested-child disagreement. Provider unavailability is runtime
status, not removal from this artifact.
