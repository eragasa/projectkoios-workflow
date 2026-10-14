# Terminal delivery and companion evidence

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Terminal-delivery requirements and companion evidence

A `WorkflowTerminalDeliveryRequirement` MUST bind exactly one admitted terminal
classification to:

- one exact primary terminal-output-port identity and its payload-reference
  schema/codec contract;
- an immutable ordered tuple of zero or more
  `WorkflowTerminalCompanionEvidenceRequirement` records;
- a maximum total companion-reference count;
- the exact canonical mapper-input ordering profile;
- the exact correlation-validation descriptor identity; and
- a requirement contract version.

Every admitted terminal classification in a child export MUST have exactly one
terminal-delivery requirement. A classification that requires no companion
MUST declare an empty companion tuple and maximum count zero rather than relying
on an omitted default. Requirements are semantic export content: adding,
removing, reordering, or changing one MUST change the child export identity and
its compiled execution-plan identity. Requirements MUST NOT add a place, arc,
transition, token, or marking to the flat child CPN.

Each `WorkflowTerminalCompanionEvidenceRequirement` MUST contain:

- an identity and a zero-based signed integer ordinal;
- an exact evidence-role identity;
- exact owner, payload-schema, codec, and media-type identities;
- maximum payload bytes;
- minimum and maximum reference cardinalities;
- one closed production phase;
- one exact correlation-predicate descriptor identity; and
- a requirement contract version.

Ordinals MUST be the contiguous sequence beginning at zero. Cardinalities MUST
be nonnegative signed 64-bit integers, minimum MUST NOT exceed maximum, and each
requirement maximum MUST be positive. Maximum payload bytes MUST be a positive
signed 64-bit integer. The enclosing maximum total companion count MUST equal
the overflow-checked sum of the requirement maxima and remain within the
representation-profile bound. A required companion has minimum cardinality
greater than zero. One reference occurrence MUST NOT satisfy two requirement
occurrences, and duplicate companion-reference identities in one delivery are
invalid.

The admitted production phases are:

- `pre_terminal_retained`: retained and admitted before the child terminal
  commit; and
- `post_terminal_pre_delivery_retained`: produced only after the exact terminal
  outcome and history head are retained, and before delivery commit.

A post-terminal companion is runtime evidence, not a second terminal-port token.
Its production MUST NOT reopen or mutate the child marking. If producing or
retaining it requires a protected operation, the runtime MUST first retain an
idempotent effect intent and then require its own exact attempt-bound authority,
execution evidence, and ambiguity/reconciliation handling.

For one candidate delivery, the runtime MUST first admit the exact primary
terminal payload reference through its port contract and every companion through
its exact companion requirement. Resolution, byte verification, canonical
decoding, and owner-invariant
validation occur before mapper invocation. The pure output mapper receives the
exact admitted primary reference, the canonical ordered companion references,
and only the bounded decoded typed values and occurrence context declared by its
descriptor. It MUST NOT call a resolver, artifact store, codec, provider,
registry, filesystem, network, clock, worker, or CPN kernel.

The canonical mapper-input sequence MUST be:

1. the primary terminal payload at sequence position zero; then
2. companion requirements in ascending requirement ordinal; and
3. within each requirement, admitted references in lexical
   `WorkflowDomainPayloadReferenceIdentity` order.

The retained sequence MUST include each requirement identity, requirement
ordinal, within-requirement ordinal, role, and exact reference identity. Each
correlation-predicate descriptor MUST declare the exact decoded fields and
expected identity sources it compares. A post-terminal requirement MUST at least
correlate the child export/plan, run, net instance, terminal classification,
outcome, and terminal history head; the parent binding MUST additionally
correlate the intended parent occurrence and reservation. The runtime MUST reject
missing, excess, duplicate, wrong-role, wrong-schema, wrong-codec,
wrong-media-type, wrong-phase, noncanonical-order, stale, cross-child, or
correlation-failing evidence. Equal payload bytes or lexical similarity do not
satisfy correlation.

`WorkflowTerminalDelivery` MUST be durably retained before parent firing. Its
content-derived identity MUST bind at least:

- the child export and execution-plan identities;
- child run and net-instance identities;
- terminal classification, primary terminal port, terminal outcome, and exact
  terminal history head;
- the exact primary payload-reference identity;
- the complete canonical companion-input sequence above;
- terminal-delivery requirement, correlation-validator, and output-mapper
  descriptor identities;
- the intended parent run, net instance, transition occurrence, selected
  binding, and reservation evidence; and
- the delivery contract version.

The actual primary and companion references are post-plan evidence and MUST NOT
be embedded into the child export, parent plan, or their identities. The export
and plan contain requirements and descriptors only. The delivery MUST NOT bind
the future parent firing result or successor marking. Parent firing evidence
MUST instead bind the already-derived delivery identity, preserving an acyclic
identity graph.
