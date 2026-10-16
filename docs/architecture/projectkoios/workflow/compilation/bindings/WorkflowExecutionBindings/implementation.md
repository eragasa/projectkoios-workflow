# `WorkflowExecutionBindings` implementation

## Responsibility

Represent bindings as frozen descriptors and opaque service handles with
canonical serialization. Keep live process-local implementations in isolated
worker or runtime tables keyed by retained binding identity.

A pure atomic Task binding retains the exact firer and result-mapping identities
selected by the plan. The linker verifies exact manifest agreement and cannot
choose another semantic mapping. An effectful binding similarly closes its
accepted lifecycle capabilities. A workflow-backed binding closes the child
plan, deployment, input/export mapping, and terminal-delivery identities.

For the existing QE artifact-set candidate, linking distinguishes the opaque
`artifact_set_identity` output from canonical `artifact_set` evidence and never
uses an evidence digest as owner identity. QE-specific and VASP-specific
execution resources remain outside generic bindings.

The current experimental bindings retain their existing identity domains and
strict SDK round trips. Complete validation must additionally reject Task-kind
substitution, stale capability digests, unsupported protocol versions, reordered
bindings, child-plan mismatch, missing child delivery guarantees, and provider
or child unavailability disguised as definition change.
