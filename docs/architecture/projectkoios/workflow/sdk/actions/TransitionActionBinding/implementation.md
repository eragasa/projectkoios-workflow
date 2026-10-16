# `TransitionActionBinding` implementation

## Responsibility

The experimental service-side boundary exposes immutable request coordinates, a
selected-binding encoder and evidence record, a firing-request factory, mapping
descriptor metadata, and a pure result-conversion method under
`projectkoios.workflow.actions`.

`ExperimentalWorkflowSelectedBindingEvidence` consumes one exact successful
shadow-CPN enablement and selection pair. It requires matching enablement and
ordering identities, proves that the selected binding occurs in the enabled set,
and content-identifies the selection result, adapter-profile identity, canonical
binding byte length, and binding-byte SHA-256. The shadow CPN source remains
provenance-bound and byte-identical; this Workflow-owned adapter evidence does
not redefine its internal identity preimages.

The private selected-binding profile uses bounded canonical UTF-8 JSON with an
explicit schema identity, transition identity, ordered assignments, variable
identities, closed value-kind tags, signed integers encoded as decimal strings,
finite reals encoded with `float.hex()`, and string sequences encoded as ordered
arrays. The factory derives the exact byte SHA-256 and does not accept a claimed
selected-binding digest. It accepts the selected-binding evidence rather than a
bare binding, requires its definition, transition, and predecessor marking to
match the SDK binding and request coordinates, and validates transition/firer
descriptors, role order, input metadata and bounds, runtime coordinates, and an
SDK codec round trip.

`ExperimentalWorkflowPureActionInputMappingDescriptor` assigns each ordered SDK
input role an opaque source kind, source-representation profile, and mapping
version. The input-extended plan and deployment candidates content-identify the
ordered descriptor tuple without changing the identity algorithm of previously
retained plan records. Runtime source evidence binds a path-free opaque source
identity to exact SDK payload metadata, byte length, and payload SHA-256. The
admission factory requires exact mapping order and payload contracts and closes
the input plan, deployment binding, selected-binding evidence, runtime
coordinates, source evidence, and resulting SDK request under one identity.
Workflow does not parse the payload.

This admission is structural evidence, not proof that a source repository owns
the claimed source identity. The input-authorization service resolves only
opaque references through a nominal owner/source repository and constructs SDK
inputs from the returned bytes. The reservation service reloads those sources
and rejects reference, revision, evidence, or payload changes. The current v0
reservation shape binds the authorization identity; earlier v0 experimental
shapes remain reconstructable under their original identity domains. No private
owner locator or owner-storage implementation enters the plan or Workflow
persistence.

The output mapping descriptor content identity closes the exact canonical SDK
transition binding and firer descriptor, mapping version, decoder profile,
output role, external variable, and `STRING` value kind.

The mapper checks the retained `OccurrenceContext`, including selected-binding
digest and predecessor revision, by exact equality; request, result, occurrence,
attempt, firer, definition, transition, and binding correlation; canonical SDK
round trips; schema and codec identity; representation; media type; exact role
order; collection limits; payload digests; and byte bounds before producing a
candidate external binding. Equality with the retained context is not current predecessor revalidation;
that remains a `WorkflowEngine` responsibility. The experimental invocation
service now performs source and predecessor revalidation before and after owner
invocation and calls this mapper only for a canonically admitted current SDK
success.

A logical-identity scalar mapping must be explicit rather than inferred from an
arbitrary owner document. For the QE SCF artifact-set direction, the accepted
`artifact_set_identity` bytes are strict, bounded canonical ASCII with no
leading or trailing whitespace, controls, machine paths, or trailing bytes. The
mapping constructs a `STRING` CPN value without importing an owner class or
parsing the canonical artifact-set evidence document.

The full `artifact_set` document remains correlated evidence. Its SHA-256 binds
exact bytes for integrity, retention, and replay; it is never promoted to the
owner logical identity merely because it is available in the SDK envelope.

Focused verification covers changed selected-binding assignment order, kind, or
value; wrong selected transition; oversized values or identities; wrong input
role, codec, or bound; predecessor-coordinate changes; wrong transition context;
stale predecessor revision or selected-binding digest; changed mapping content;
mismatched result correlation; malformed scalar encoding; wrong output role or
codec; unregistered output variable; reordered or missing evidence; private
locator; payload-digest substitution; and oversized result cases. Output-color
compatibility still belongs to definition validation and pure CPN firing. No
live binding instance belongs in a durable execution plan; only its versioned
descriptor and content identity do.

The reviewed Simulations pilot emits `artifact_set_identity` as its sole
external-state output and retains `artifact_set` as evidence. The experimental
Workflow mapper does not alter the standalone SDK `0.1.0a1` contract or claim
complete `WorkflowExecutionPlan`, `WorkflowExecutionBindings`, Task/Workflow,
or CPN-bindings conformance. The bounded execution chain now correlates the
mapped result with exact CPN state, invokes the pure CPN firer, and atomically
retains compact commit, CPN replay evidence, lifecycle transition, reservation
consumption, and marking advancement. Those later phases remain WorkflowEngine
responsibilities rather than mapping authority.
