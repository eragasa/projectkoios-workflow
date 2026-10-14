# Binding payload references to CPN colors

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Binding payload references to CPN colors

## `WorkflowPayloadColorBinding`

The execution plan MUST contain one `WorkflowPayloadColorBinding` for every CPN
color that carries domain payload references. The binding MUST identify:

- exact flat CPN definition and color identities;
- exact allowed CPN value kind, which MUST be `STRING`;
- owner, payload schema, codec, and media-type identities;
- maximum payload bytes;
- `maximum_reference_tokens_per_complete_marking` for this color across all
  places in one complete marking;
- whether every token requires an individual token identity; and
- binding contract version.

The v0.1 count is a per-complete-marking bound, not a run-lifetime or history
bound. Any lifetime/history bound requires a separately named policy in a later
contract version.

For authoritative action, event, result, handoff, authority, and decision
records, individual token identity is REQUIRED. Anonymous multiplicity MUST NOT
represent individually meaningful occurrences or evidence.

A reference token's CPN string value MUST be the exact
`WorkflowDomainPayloadReferenceIdentity`. The complete reference record MUST be
retained in the execution or event evidence needed to reconstruct the marking.
A raw JSON body, artifact path, or owner-native record serialized into the token
string is invalid.

Before first admission of a reference token into a run marking or external
output binding, the runtime adapter MUST resolve the retained reference and
require:

- exact canonical reference bytes and reference identity;
- `schema_identity` and `media_type` equal to the color binding;
- exactly one owner and codec resolution selected by that binding;
- `byte_size` no greater than the binding's maximum payload bytes;
- payload bytes whose actual size and SHA-256 equal the reference;
- successful decoding and owner-invariant validation by that exact codec;
- the candidate complete initial or successor marking containing no more than
  `maximum_reference_tokens_per_complete_marking` tokens of that color across
  all places; and
- a non-null exact token identity for every such token when the binding requires
  individual identity, with no duplicate required identity in the complete
  marking.

The same count and token-identity checks apply to externally supplied output
bindings before they may contribute to a candidate successor marking. The
runtime MUST retain payload-admission evidence correlated to the reference,
color binding, execution plan, and run. Later pure CPN enablement and firing use
the already-admitted reference token and MUST NOT repeat artifact resolution.
Replay MUST independently repeat the same reference/binding/codec/count/token-
identity checks before pure CPN replay. A schema, media-type, owner, codec, size,
count, missing-identity, or duplicate-identity mismatch fails closed before the
candidate marking is admitted.

The payload-color binding belongs to `WorkflowExecutionPlan` and contributes to
its identity. It does not extend `CpnColorDefinition` or allow the
flat kernel to import owner types.

If a guard needs an accepted/rejected state or another bounded fact derived from
a payload, the owner MUST admit it through an explicit scalar/status color or a
closed field in an admitted bounded control record, normally produced by a prior
guarded acceptance transition. Resolving a reference during guard evaluation is
prohibited. Existing source records MAY be mapped one-for-one to bounded control
records when preserving their original field guards is required; the mapping
MUST NOT become an excuse to copy a payload body into the kernel.
