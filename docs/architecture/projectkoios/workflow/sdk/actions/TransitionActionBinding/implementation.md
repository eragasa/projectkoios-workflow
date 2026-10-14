# `TransitionActionBinding` implementation

## Responsibility

The eventual SDK mapping boundary should expose immutable descriptor metadata
and pure request/result conversion methods. A validating base must check
`OccurrenceContext`, selected-binding digest, action version, schema and codec
identity, representation, media type, role order, collection limits, and payload
bounds before producing a candidate external binding.

A logical-identity scalar mapping must be explicit rather than inferred from an
arbitrary owner document. For the QE SCF artifact-set direction, the accepted
`artifact_set_identity` bytes are strict, bounded canonical ASCII with no
leading or trailing whitespace, controls, machine paths, or trailing bytes. The
mapping constructs a `STRING` CPN value without importing an owner class or
parsing the canonical artifact-set evidence document.

The full `artifact_set` document remains correlated evidence. Its SHA-256 binds
exact bytes for integrity, retention, and replay; it is never promoted to the
owner logical identity merely because it is available in the SDK envelope.

Conformance must cover wrong transition, stale marking, changed action version,
mismatched owner request/result, malformed scalar encoding, wrong role or codec,
unregistered output variable or color, reordered evidence, private locator, and
oversized result cases. No live binding instance belongs in a durable execution
plan; only its versioned descriptor and content identity do.

The reviewed Simulations pilot now emits `artifact_set_identity` as its sole
external-state output and retains `artifact_set` as evidence. Publishing the
Workflow-owned mapping remains separate work and does not alter the standalone
SDK `0.1.0a1` contract by implication.
