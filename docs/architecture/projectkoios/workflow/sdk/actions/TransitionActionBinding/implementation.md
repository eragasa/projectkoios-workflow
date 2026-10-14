# `TransitionActionBinding` implementation

## Responsibility

The experimental service-side mapping boundary exposes immutable descriptor
metadata and a pure result-conversion method under
`projectkoios.workflow.actions`. Its content identity closes the exact canonical
SDK transition binding and firer descriptor, mapping version, decoder profile,
output role, external variable, and `STRING` value kind.

The mapper checks the retained `OccurrenceContext`, including selected-binding
digest and predecessor revision, by exact equality; request, result, occurrence,
attempt, firer, definition, transition, and binding correlation; canonical SDK
round trips; schema and codec identity; representation; media type; exact role
order; collection limits; payload digests; and byte bounds before producing a
candidate external binding. Equality with the retained context is not current
predecessor revalidation; that remains a `WorkflowEngine` responsibility.

A logical-identity scalar mapping must be explicit rather than inferred from an
arbitrary owner document. For the QE SCF artifact-set direction, the accepted
`artifact_set_identity` bytes are strict, bounded canonical ASCII with no
leading or trailing whitespace, controls, machine paths, or trailing bytes. The
mapping constructs a `STRING` CPN value without importing an owner class or
parsing the canonical artifact-set evidence document.

The full `artifact_set` document remains correlated evidence. Its SHA-256 binds
exact bytes for integrity, retention, and replay; it is never promoted to the
owner logical identity merely because it is available in the SDK envelope.

Focused verification covers wrong transition context, stale predecessor revision
or selected-binding digest, changed mapping content, mismatched result
correlation, malformed scalar encoding, wrong role or codec, unregistered output
variable, reordered or missing evidence, private locator, payload-digest
substitution, and oversized result cases. Output-color compatibility still
belongs to definition validation and pure CPN firing. No live binding instance
belongs in a durable execution plan; only its versioned descriptor and content
identity do.

The reviewed Simulations pilot emits `artifact_set_identity` as its sole
external-state output and retains `artifact_set` as evidence. The experimental
Workflow mapper does not alter the standalone SDK `0.1.0a1` contract, implement
`WorkflowExecutionPlan` or `WorkflowExecutionBindings`, revalidate or reserve a
marking, persist evidence, or invoke the CPN firer.
