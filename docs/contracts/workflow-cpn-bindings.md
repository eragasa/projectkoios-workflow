# Canonical CPN payload and hierarchical binding contract

## Contract metadata

| Field | Value |
|---|---|
| Contract ID | `projectkoios.workflow.cpn-bindings` |
| Target version | `0.1.0` |
| Status | Proposed architecture contract; no implementation binding |
| Specification revision | Git commit containing this document |
| Owner | `projectkoios-workflow` |
| Acceptance authority | Project Koios operator after workflow-owner and materially affected adapter/consumer review |
| Dependencies | `projectkoios.workflow.core@0.1.0` (Proposed); `projectkoios.workflow.runtime@0.1.0` (Candidate) |
| Consumers | CPN compiler and runtime adapters; managed-project adapters; child-workflow providers |
| Implementation bindings | None |
| Compatibility | Unknown while proposed |
| Effective baseline | None while proposed |

## Status

This document specifies the owner-side architecture required for canonical CPN
payload references and runtime nesting of separately owned child workflows. It
is a proposal, not an available Python API, implementation authorization,
dependency authorization, provider migration, execution grant, release, or
compatibility promise.

The existing `projectkoios.workflow.petrinet.colored` package is a
non-authoritative shadow kernel. It supplies useful evidence for immutable flat
CPN definitions, markings, enablement, selection, and pure firing, but it does
not implement this contract. In particular, its current `CpnValue` model admits
only scalar values and a string sequence, and its current `CpnValueExpression`
admits only literals and whole variables. It does not implement the bounded
control-record, field-projection, or record-construction contract below. The
current local runtime implements only its bounded effect-free Slice A and does
not implement child launch, payload resolution, attempts, dispatch,
cancellation, reconciliation, or quiescence.

## Normative scope and vocabulary

The normative contract begins at **Architectural decision** and continues
through **Stop conditions**, except text explicitly labeled informative,
example, rationale, current evidence, or deferred decision.

The capitalized words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**,
**SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and
**OPTIONAL** have their meanings from the Project Koios contract-governance
policy.

Names in backticks identify required conceptual records and operations. Their
final source modules and class names MAY change before acceptance only if an
explicit mapping preserves every field, invariant, and conformance vector in
this document. No consumer may treat these names as currently importable.

## Purpose

A managed-project CPN needs to carry references to owner-defined typed records
without embedding arbitrary JSON or importing domain classes into the generic
kernel. It also needs to invoke an authoritative child workflow without copying
that child's topology into the parent or creating a hidden imperative task
engine.

This contract defines:

- content-addressed references to immutable owner payloads;
- the boundary between generic CPN token values and owner codecs;
- the definition-closure binding from CPN colors to payload schemas;
- runtime nesting of separately compiled flat child CPNs;
- exact parent/child occurrence, attempt, authority, outcome, primary terminal
  payload, companion evidence, and delivery correlation;
- persistence, replay, cancellation, reconciliation, and quiescence rules; and
- a generic retained staging-receipt barrier for provenance-sensitive effects.

It does not define scientific schemas, calculator formats, artifact-store
implementation, provider-native job identity, or managed-project acceptance
policy.

## Architectural decision

### Flat CPN semantics and runtime nesting

Each executable net instance MUST use one immutable, validated, flat CPN
definition and one complete marking. Reusable control fragments MAY be lowered
at compile time into that flat definition.

A child workflow is different from a compile-time fragment. A child remains a
separately compiled workflow plan with its own flat CPN definition, marking,
run, occurrences, attempts, history, and terminal outcome. The parent plan
references the child through a typed hierarchical binding. The child topology
MUST NOT be copied into the parent definition.

This is runtime nesting of separately authoritative CPN instances, not a claim
to implement the hierarchical CPN formalism of CPN Tools.

### Definition layers

The contract distinguishes three identities:

1. `CpnDefinitionIdentity` is the owner-local nominal identity of
   the flat generic CPN graph; it is not sufficient content closure.
2. `WorkflowExecutionPlanIdentity` identifies the complete executable semantic
   closure: exact canonical flat-CPN representation identity and digest, exact
   CPN execution-profile identity, initial-marking contract, payload-color
   bindings, transition routes, child bindings, terminal-delivery requirements,
   mapping descriptors, and compiler implementation/version descriptors.
3. `WorkflowExecutionBindingsIdentity` identifies one exact deployment linking
   of that plan to provider, worker, environment, resolver, and child-plan
   descriptors.

The execution-plan identity MUST be the domain-separated SHA-256 of one closed
canonical plan representation containing every semantic-closure item above. The
deployment-bindings identity MUST similarly derive from one closed canonical
binding representation and the exact execution-plan identity. Neither identity
may be caller-supplied nominal text, a mutable registry key, or an import path.
The canonical representation profiles are private candidate boundaries until a
separate compatibility decision accepts them.

A provider or environment change MUST NOT mutate the execution plan. A canonical
flat-definition byte, representation profile, CPN execution-profile identity,
payload schema, codec, transition mapping, child export, child port,
terminal-delivery requirement, companion-evidence requirement, or child-plan
change MUST change the execution-plan identity even when a nominal
`CpnDefinitionIdentity` is unchanged.

### Canonical flat definition and CPN execution profile

The plan MUST bind an immutable canonical flat-definition representation, its
representation-profile identity, and SHA-256 over its exact bytes. The canonical
representation MUST close over every semantic color, place, transition, arc,
variable, pattern, expression, priority, and selection-policy field. A nominal
`CpnDefinitionIdentity` alone is insufficient because the current
shadow kernel accepts it separately from graph content.

The plan MUST also bind one immutable `WorkflowCpnExecutionProfile` containing
exact identities for:

- admitted CPN value model, bounded control-record representation, and semantic
  version;
- closed expression grammar, including exact field-projection and
  control-record-construction variants;
- canonical definition representation and decoding;
- canonical marking, transition-binding, directive, and result representation
  and identity derivation;
- definition validation;
- marking and control-record-schema validation;
- expression and constructor evaluation;
- complete enabled-binding enumeration;
- enabled-binding ordering;
- binding selection;
- external-output validation; and
- transition firing.

Changing any profile identity MUST change the execution-profile identity and the
execution-plan identity. Replay MUST use the exact retained profile; current
registry defaults or implementation-local constants are insufficient semantic
closure.

Post-hoc validation evidence MAY bind the already-derived plan and profile
identities, but MUST NOT become an input to either identity.

### Bounded generic control records

Contract v0.1 admits one additional generic CPN value kind, `CONTROL_RECORD`,
for small immutable control-plane records whose fields are required by guards or
pure output construction. A control record is kernel state, not a domain payload
body or an artifact envelope.

Each `CpnControlRecord` MUST contain exactly:

- one `CpnControlRecordTypeIdentity`; and
- one immutable tuple of `CpnControlRecordField` values.

Each field MUST contain one bounded field identity and one already-admitted CPN
value. A record field MAY contain another `CONTROL_RECORD`, but the complete
value MUST form a finite immutable tree. It MUST NOT contain a mapping, arbitrary
object, callable, class, module, import path, source expression, byte buffer,
payload body, artifact resolver, store handle, credential, filesystem path, or
provider-native live value.

The canonical flat definition MUST contain every
`CpnControlRecordTypeDefinition` used by a color, literal, projection, or
constructor. A type definition MUST declare:

- its exact type identity and contract version;
- its complete required field set;
- for every field, the exact scalar value kind or nested control-record type;
  and
- whether a string field is a scalar/status value or an admitted immutable
  reference identity; and
- for a reference field, the exact reference-kind/role identity and lexical
  contract required before record admission.

All fields are required in v0.1; optional fields, open records, union fields, and
additional properties are unsupported. Record-type references MUST form a
finite acyclic graph. A color admitting `CONTROL_RECORD` MUST name every exact
record type admitted at that color. The record type definitions and color/type
admissions are semantic flat-definition content and contribute to the canonical
definition digest and execution-plan identity.

The private v0.1 control-record bounds are:

| Item | Bound |
|---|---|
| Record type identity | `1..512` printable ASCII bytes, no controls, DEL, or leading/trailing whitespace |
| Record type definitions per flat definition | `0..256` |
| Field identity | `1..128` ASCII bytes matching `[A-Za-z][A-Za-z0-9_]{0,127}` |
| Fields per record or constructor | `1..64`, unique and stored in lexical field-identity order |
| Control-record nesting depth | `1..8`, with the root record at depth one and scalar fields adding no depth |
| Total record and scalar nodes in one value | `1..256` |
| Expression-tree depth | `0..64`, with a literal or variable at depth zero |
| Expression nodes per transition | `0..4096` across guards and inscriptions |
| One string field | `0..4096` UTF-8 bytes; no normalization or case folding |
| One string-sequence field | `0..256` entries, each `1..4096` UTF-8 bytes |
| Canonical encoded control-record value | `1..65536` bytes |

Existing scalar invariants continue to apply: integers are exact signed 64-bit
values, Booleans are not integers, reals are finite binary64 values under the
exact retained representation profile, and `NONE` is exact null. Scientific
arrays, matrices, native output, unrestricted prose, and provider records that
exceed these bounds remain owner payloads referenced by admitted immutable
reference identities. A reference field is admitted only after its outer
reference contract and correlation are validated; retaining the reference string
inside a control record grants no payload resolution or authority. The complete
reference record remains outside the kernel. A complete scientific observation
MUST NOT be copied into a control record merely because a few Boolean guard
facts are needed.

Canonical control-record bytes MUST use one exact tagged representation selected
by the retained CPN value-model profile. The representation MUST distinguish
record type, field identity, scalar kind, nested record, integer, Boolean, real,
string, string sequence, and null without relying on host-language class names
or JSON-number inference. Decoding MUST reject duplicate, missing, unknown,
wrongly typed, noncanonical, cyclic, over-depth, over-node, over-field, and
oversized values before marking admission, then reconstruct and re-encode the
typed value and require byte-for-byte equality.

### Closed field projection and record construction

`CpnValueExpression` v0.1 MUST be a closed tagged grammar with exactly these
variants:

1. `LITERAL`: one exact admitted `CpnValue`;
2. `VARIABLE`: one whole definition-declared bound variable;
3. `FIELD_PROJECTION`: one record-producing base expression and a nonempty tuple
   of `1..8` field identities traversed in order; and
4. `CONTROL_RECORD_CONSTRUCTOR`: one exact record-type identity and one
   constructor field expression for every required field of that type.

A constructor's field identities MUST be unique and stored in lexical order.
Its field set MUST equal the declared record type exactly. Every field expression
MUST evaluate to the declared scalar kind or nested record type. Projection MUST
start from an admitted control record and each path step MUST exist with the
exact declared type. Missing fields, wrong record types, wrong result kinds,
constructor omissions or additions, and bound failures are closed expression-
evaluation failures; they MUST NOT be repaired, treated as a false guard, or
resolved through a domain callback.

The grammar has no generic function-call, method-call, attribute traversal,
subscript, comprehension, lambda, source-text expression, reflection, import,
`eval`, or owner-class constructor node. A provider-owned constructor mapping
MAY map one reviewed domain constructor identity to one closed
`CONTROL_RECORD_CONSTRUCTOR` tree before compilation. The compiled definition
contains only the generic record type and expression tree, never the callable or
import path. An outer typed adapter MAY translate between an owner record and an
admitted control record before marking admission or after pure firing, but that
adapter identity, version, exact mapping descriptor, input/output record types,
and bounds MUST contribute to the execution plan.

`WorkflowCpnExecutionProfile` MUST bind distinct exact identities for:

- `CpnValueModelIdentity`, including the scalar and control-record canonical
  representation and every bound above;
- `CpnExpressionGrammarIdentity`, including every admitted expression variant
  and path/constructor rule;
- `CpnControlRecordSchemaValidatorIdentity`;
- `CpnExpressionEvaluatorIdentity`, including projection and constructor
  evaluation;
- `CpnExternalOutputValidatorIdentity`; and
- the existing definition validator, marking validator, complete enabler,
  ordering, selector, and firer identities.

The profile identity MUST derive from these exact component identities and their
semantic versions. Changing a record bound, record type rule, field ordering,
path rule, constructor rule, mapping descriptor, validator, evaluator, or value
representation MUST change the applicable component identity, CPN execution-
profile identity, and execution-plan identity.

For the simulations SCF compatibility fixture, the owner adapter MAY represent
each existing small action, event, request, start, analyzed-output, and terminal
outcome object as exactly one typed control-record token. The analyzed-output
record may carry bounded `task_id`, `completed`, and `converged` guard fields plus
an immutable normalized-observation reference identity; the full observation
remains an owner payload. Field projections preserve the existing evaluation-ID,
task-ID, completion, and convergence guards. Record constructors preserve the
existing registration, submission, analysis, success, and known-failure outputs.
The adapter MUST NOT split one source token into several topology-visible fact
tokens, move a source guard into pre-admission policy, add a place or transition,
or call a domain constructor inside the kernel. This is the required route to
parity with the unchanged twelve-place/eight-transition topology.

### Consumer-vocabulary reconciliation

The Si-VC consumer profile uses *definition identity* for the complete semantic
closure. Under this owner contract, that term maps to
`WorkflowExecutionPlanIdentity`. It does not expand
`CpnDefinitionIdentity`, which remains the identity of the flat CPN
semantics only. Consequently:

- managed-project payload-schema and child-interface references change the
  execution-plan identity;
- a child binding names the parent flat CPN definition and transition, then the
  enclosing plan names the child binding;
- the binding MUST NOT name the enclosing plan from which its own identity is
  derived;
- post-hoc plan/export evidence binds the already-derived semantic identity and
  MUST NOT be embedded back into that identity; and
- the resulting content-identity graph remains acyclic.

The consumer phrase *firing the substitution transition creates a child launch*
maps to selection and durable reservation of the nested parent occurrence. The
parent's logical CPN firing commits only after an exact accepted child terminal
delivery. This separation preserves pure CPN firing and prevents a launch
request from masquerading as a child result.

### No hidden semantic callbacks

The generic CPN kernel MUST evaluate only its closed admitted value kinds,
guards, inscriptions, markings, and bindings. Kernel enablement or firing MUST
NOT call an artifact store, payload codec, domain object, registry, provider,
worker, clock, network service, or filesystem.

Facts needed by a guard MUST already be explicit scalar/status values or fields
of an admitted bounded control-record token in the marking. A field projection
MUST traverse only that immutable admitted control record. A guard MUST NOT
fetch a referenced payload, inspect payload fields, invoke an owner object, or
call an arbitrary callback.

## Content-addressed domain payloads

### `WorkflowDomainPayloadReference`

`WorkflowDomainPayloadReference` is the complete generic reference to one
immutable owner payload. To preserve the selected managed-project profile, it
MUST contain exactly these six fields and no generic envelope fields:

| Field | Requirement |
|---|---|
| `payload_identity` | Bounded owner-defined nominal identity of the typed value |
| `schema_identity` | Exact owner schema family and major version |
| `media_type` | Bounded registered JSON media type |
| `sha256` | 64 lowercase hexadecimal digits over the exact payload bytes |
| `byte_size` | Positive signed 64-bit integer |
| `artifact_identity` | Opaque immutable artifact-store identity |

Owner, codec, and contract-version identities belong to the compiled
`WorkflowPayloadColorBinding`, not this reference. The reference MUST NOT
contain payload bytes, a decoded mapping, credentials, private source text,
executable code, a mutable store handle, or a filesystem path.

The `WorkflowDomainPayloadReferenceIdentity` MUST be derived as:

```text
projectkoios.workflow.payload-reference:1:<sha256(canonical-reference-bytes)>
```

The identity is not embedded in the reference document and therefore introduces
no self-reference. `sha256` identifies the owner payload bytes;
`WorkflowDomainPayloadReferenceIdentity` identifies the complete reference
record. They MUST remain distinct.

SHA-256 establishes byte correlation only. It does not establish producer
authenticity, chronology, semantic validity, authorization, scientific
acceptance, or publication status.

### Identity and text bounds

Payload, schema, and artifact identities MUST be nonempty bounded ASCII
strings, exclude controls, and contain at most 512 bytes. The media type MUST
satisfy its registered JSON or vendor-tree grammar and the same size/control
bounds; its required `/` separator is not path syntax. The reference document
MUST contain at most 4096 bytes. `byte_size` MUST be greater than zero and no
greater than the owner schema's registered limit.

An artifact identity is an opaque locator under an artifact-owner contract. It
MUST NOT be a path beginning with `/`, `~/`, `\\`, `file:`, or a drive-letter
prefix. Resolving it to a machine locator belongs to an isolated resolver or
worker, never to the CPN kernel.

### Canonical reference JSON

The reference document MUST use this private canonical JSON profile:

- one top-level JSON object;
- UTF-8 without a byte-order mark;
- no leading or trailing bytes and no trailing newline;
- the exact closed field set above;
- object keys sorted lexically;
- compact `,` and `:` separators;
- non-ASCII characters emitted directly rather than ASCII-escaped;
- strings, signed 64-bit integers, exact Booleans, `null`, arrays, and objects
  only; and
- no binary64 JSON numbers, decimal extensions, `NaN`, or infinities.

The reference encoding MUST be byte-equivalent to the applicable value passed
to:

```python
json.dumps(
    value,
    ensure_ascii=False,
    allow_nan=False,
    separators=(",", ":"),
    sort_keys=True,
).encode("utf-8")
```

A structural reference decoder MUST reject duplicate keys, unknown keys,
missing keys, invalid UTF-8, unsupported reference-profile versions, invalid
field types, noncanonical bytes, over-limit content, inconsistent field values,
and a claimed reference identity that differs from the canonical reference-byte
digest. After typed construction, it MUST re-encode and require byte-for-byte
equality.

Digest and byte-size agreement with the owner payload can be checked only when
those payload bytes are supplied. Full reference validation MUST require exact
`byte_size` and SHA-256 agreement before owner decoding or token admission.

This profile is a private candidate boundary, not a public compatibility
promise.

### Owner payload bytes

The payload itself remains an owner artifact. The exact codec identity bound to
`schema_identity` in the execution plan determines canonical byte and typed
decoding rules. A codec claiming
`projectkoios.workflow.canonical-json-control:1` MUST apply the same JSON rules
above and MUST restrict control/provenance values to `null`, exact Booleans,
strings, signed 64-bit integers, arrays, and objects.

Scientific binary64 arrays, matrices, native files, and large manifests MUST
remain in owner formats with explicit codecs and artifact references. They MUST
NOT acquire an implicit JSON-number convention through this contract.

### `WorkflowDomainPayloadCodec`

A registered owner codec MUST provide the conceptual pure operations:

```text
encode_canonical(typed_value)
  -> payload_bytes + WorkflowDomainPayloadEncodingMetadata
assemble_reference(payload_bytes, encoding_metadata, artifact_identity)
  -> WorkflowDomainPayloadReference | closed_failure
decode_canonical(payload_bytes, reference)
  -> typed_value | closed_failure
```

`WorkflowDomainPayloadEncodingMetadata` contains the owner-derived
`payload_identity`, `schema_identity`, and `media_type`; it contains no artifact
identity. `assemble_reference` MUST compute `sha256` and `byte_size` from the
exact supplied bytes and combine them with the immutable store-provided
`artifact_identity`. It MUST NOT accept caller-claimed digest or size values.

Artifact retention is an outer effect owned by the artifact boundary:

1. the pure codec produces bytes and encoding metadata;
2. an authorized artifact operation durably retains the exact bytes and returns
   an immutable `artifact_identity`; and
3. the pure assembler constructs and validates the six-field reference.

The codec and assembler MUST:

- consume and produce immutable owner-defined typed values;
- avoid `Any`, raw mappings, and `object` as unspecified public boundaries;
- perform no filesystem, network, database, clock, random, authority, or
  calculator operation;
- strictly validate schema version, collection bounds, nominal identities,
  numeric types, and cross-field invariants;
- reject Boolean-as-number and numeric-string substitutions unless the owner
  schema explicitly defines a string representation; and
- return a closed typed failure rather than repairing input.

Generic Workflow validates and retains the reference. A runtime admission,
mapping, or replay-preverification adapter MAY invoke only the exact registered
owner codec and assembler. Generic Workflow MUST NOT fabricate an artifact
identity, interpret the owner payload's scientific or provider-specific fields,
or let the CPN kernel invoke a codec, assembler, or artifact store.

## Binding payload references to CPN colors

### `WorkflowPayloadColorBinding`

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

## Child workflow export

### `WorkflowChildDefinitionExport`

A child owner MUST publish an immutable export containing:

- owner and workflow-family identities;
- child source-definition identity and contract version;
- exact compiled child execution-plan identity and digest;
- exact nominal flat child CPN definition identity;
- exact canonical flat-definition representation identity and digest;
- exact child CPN execution-profile identity;
- initial-marking constructor descriptor identity;
- bounded typed input-port definitions;
- bounded typed terminal-output-port definitions;
- admitted terminal classifications;
- exactly one terminal-delivery requirement for every admitted terminal
  classification;
- cancellation and reconciliation capability declarations;
- protected-effect capability declarations;
- compiler/exporter implementation and version identities;
- source revision identity; and
- export contract version.

The export MUST contain no live owner, provider, registry, interpreter, SNAKES
object, callable, mutable configuration, or post-hoc evidence that identifies
the export itself.

A separate `WorkflowChildExportEvidenceBinding` MUST bind the already-derived
child-export identity to canonical conformance-evidence references. That
evidence binding MAY contribute to deployment acceptance and
`WorkflowExecutionBindingsIdentity`, but MUST NOT change or become an input to
the child-export or child-plan identity.

A child sourced from another CPN engine MAY be exported only through an
owner-controlled deterministic translator or adapter that produces canonical
flat CPN IR and conformance evidence. Field access and reviewed owner
constructors MUST lower to the closed projection and control-record-construction
grammar above; live classes, callables, and constructor import paths are invalid
canonical semantics. A constructor import path or reported place/transition
count alone is insufficient. Parameter-dependent initial markings MUST be
separated from stable topology so a run subject does not silently redefine the
child plan.

### Port definitions

Each port MUST identify:

- port identity and direction;
- exact CPN place and color identity in the child plan;
- exact payload schema/codec or admitted scalar kind;
- minimum and maximum token cardinality;
- correlation fields or reference identities required by the mapping; and
- whether the port is initial, external-event, terminal, cancellation, or
  reconciliation traffic.

Terminal ports MUST form a closed set. A terminal payload is evidence about the
child outcome; it MUST NOT implicitly assert parent-domain acceptance.

### Terminal-delivery requirements and companion evidence

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

## Parent hierarchical binding

### `WorkflowHierarchicalChildBinding`

The parent execution plan MUST contain one binding for each nested route. The
binding MUST identify:

- exact parent flat CPN definition and transition-mapping identities;
- exact child export and child execution-plan identities;
- parent input place/color and child input-port mapping descriptor;
- for every admitted terminal classification, the exact child terminal-delivery
  requirement and parent external-output mapping descriptor;
- exact primary, companion, input, and output payload schema/codec identities;
- child-instance cardinality, which MUST equal exactly one in contract v0.1;
- the sole canonical child ordinal, which MUST be signed integer `0`;
- admitted child terminal classifications;
- cancellation propagation policy identity;
- quiescence requirement;
- correlation and output bounds; and
- binding contract version.

The binding and all mapping descriptors contribute to the parent execution-plan
identity. A v0.1 compiler or linker MUST reject any child-instance cardinality
other than one or any ordinal other than `0`; child fan-out is unsupported. The
binding MUST NOT contain that enclosing execution-plan identity, because doing
so would create a content-identity cycle. The child flat topology does not become
part of the parent flat CPN definition and MUST NOT be reproduced in parent
source, plan, or deployment bindings.

Deployment linking MUST prove exact agreement among parent plan, child export,
child plan, terminal-delivery and companion requirements, mapper and correlation
descriptors, provider capabilities, protocol versions, and required child-export
evidence bindings. A deployment MUST reject an admitted classification for which
the linked provider cannot supply every required companion role in its declared
phase and bounds. The transitive child-plan/export graph MUST be finite and
acyclic; recursive child-plan references are invalid in this contract version.
Discovery by matching names, annotations, nearby registry entries, or Python
subclass relationships is prohibited.

### Child-instance identity

`WorkflowChildNetInstanceIdentity` MUST derive from at least:

- parent run and net-instance identities;
- parent execution-plan identity;
- hierarchical-binding identity;
- parent transition-occurrence identity;
- exact selected parent binding and reservation evidence; and
- the v0.1 sole canonical child ordinal `0`.

A managed project MUST NOT mint the child instance or parent occurrence
identity. A repeated CPN loop activation creates a new parent occurrence and a
new child instance. An operational retry under an unchanged occurrence creates
a new attempt and MUST NOT create another child instance while original launch
status is ambiguous.

## Nested-route runtime protocol

A nested route MUST follow this durable protocol:

1. Pure CPN enablement and selection identify one exact parent transition
   binding at one exact marking revision.
2. The runtime creates and retains the parent occurrence and exact reservation.
3. The pure input mapper produces the child initial-input references from the
   selected binding and occurrence context.
4. The runtime retains a child-creation intent and the unique child-instance
   identity before attempting child creation.
5. Child creation is idempotent for that identity. An indeterminate create
   enters reconciliation; it MUST NOT create another child instance.
6. The child starts from the exact exported plan and a validated initial marking
   correlated to the parent occurrence.
7. The parent logical transition remains reserved and unfired while the child is
   nonterminal or its classification-specific delivery is incomplete.
8. After retaining the exact terminal outcome and history head, the runtime
   selects the sole compiled terminal-delivery requirement for that
   classification.
9. The runtime durably correlates and admits the primary terminal reference and
   every required companion reference. Post-terminal production follows a
   retained idempotent intent and the normal authority/reconciliation protocol.
10. The runtime constructs and retains one identity-bound terminal delivery only
    after exact phase, cardinality, order, schema/codec, and correlation checks
    pass.
11. The pure output mapper consumes the already-admitted primary and canonical
    ordered companion inputs and produces the parent's exact external-output
    binding without resolving or decoding an artifact.
12. The runtime revalidates the reservation and atomically records the one
    parent CPN firing and terminal nested-route evidence bound to the retained
    delivery identity.

The child terminal classification MAY represent success, known failure,
cancellation, or another definition-declared terminal outcome. Each
classification has its own closed companion requirements; a success-only
companion MUST NOT be required for or fabricated on a known-failure route.
Mapping a child-workflow terminal outcome and its required evidence into a
neutral parent child-outcome token does not grant parent-domain acceptance. A
separate guarded parent transition MUST classify or accept it.

Infrastructure failure, ambiguous child creation, corrupt child history,
missing or ambiguous companion retention, mismatched delivery, unresolved
cancellation, or nonquiescent child state MUST NOT fire the parent logical
transition. Such conditions remain operational failure or reconciliation
evidence until an explicit compiled route handles them.

No runtime may inject a child result or companion directly into a parent
transition. They enter only through the retained terminal delivery, declared
external-output mapping, and normal pure firing boundary.

## Runtime identities and correlation

The runtime MUST preserve distinct nominal identities for:

| Identity | Required correlation |
|---|---|
| Workflow run | Exact execution plan, initial marking, and subject |
| Net instance | Root run or exact parent-child instance relationship |
| Request | Run, expected prior state/revision, operation intent, ordered input references, actor/authority references, bounds, and idempotency identity |
| Transition occurrence | Request plus net instance, definition, marking revision, transition, ordered binding, and exact token reservation |
| Plan | Occurrence, mapping/configuration, ordered effect intents, bounds, and runtime version |
| Effect intent | Occurrence, operation kind, exact inputs, expected evidence, and ordinal |
| Attempt | Occurrence and bounded attempt ordinal |
| Dispatch authorization | Exact occurrence, attempt, plan, intent, authority decision, scope, and validity observation |
| Execution evidence | Exact attempt, authorization, worker/provider, request, and observed result |
| Child instance | Parent occurrence, child binding, and child ordinal |
| Delivery | Exact child outcome/history head, primary terminal reference, canonical ordered companion references, requirement/mapping descriptors, and intended parent occurrence |
| Reconciliation | Exact ambiguous attempt, original idempotency/start identity, retained evidence, and query result |
| Cancellation | Exact target instance/attempt, authority, request identity, and observed result |
| Quiescence | Exact admitted child, attempt, and terminal-delivery assembly set with terminal/reconciled evidence |

Identity derivations MUST be acyclic. Logical identities, payload-reference
identities, artifact digests, and execution-evidence identities MUST remain
distinct even when one record references all of them.

A delivery from another definition, child instance, occurrence, attempt,
terminal history head, parent occurrence, terminal-delivery requirement,
companion requirement, correlation descriptor, or mapping descriptor MUST be
rejected or routed to reconciliation. A missing, excess, stale, cross-child,
wrong-phase, or ambiguously retained companion has the same fail-closed result.
Lexical similarity and equal domain payloads are insufficient correlation.

## Authority and protected effects

Child creation does not transfer or manufacture effect authority. Every
protected effect in a child MUST receive its own Workflow-verified, exact
occurrence-and-attempt dispatch authorization under the runtime contract.
Parent authority MUST NOT be inherited by child transitions unless the external
authority owner explicitly issued matching separately scoped evidence.

An authority admission MUST be single-use and bind exact plan, effect intent,
attempt, worker/provider scope, inputs, limits, and validity observation.
Possession of a payload reference, child export, executable path, manifest,
prior result, test marker, or enabled token does not grant authority.

Cancellation that may affect an external process is a separate protected
operation. Missing acknowledgement, timeout, lease expiry, worker loss, or
parent termination is not proof that cancellation or non-execution occurred.

## Artifact resolution and staging receipts

### Resolver boundary

The control plane and CPN kernel retain only typed content-addressed references.
An isolated authorized worker resolves artifact identities to provider-local
locators. The worker MUST verify the resolved source against the retained
reference before using it and MUST NOT return private paths in canonical
Workflow events or CPN tokens.

### `WorkflowArtifactStagingReceipt`

A plan MAY declare a
`WorkflowArtifactStagingReceiptRequirement` before dispatch of a dependent
effect. The immutable requirement descriptor binds the permitted receipt schema
and codec, source roles, staging effect-intent ordinal, dependent effect-intent
ordinal, validation predicate, and contract version. The plan and dependent
effect intent name this requirement identity only; they MUST NOT name a future
actual receipt.

Staging that writes a workspace is itself an effect intent and requires its own
applicable attempt-bound authority under the owning policy. After staging, the
typed receipt payload MUST bind:

- receipt schema and codec identities;
- exact staging-receipt requirement identity;
- source accepted-parent or source-set payload reference;
- source manifest payload reference;
- dependent occurrence, request, plan, and attempt identities;
- exact staging effect-intent and dependent execution effect-intent identities;
- staging authority identity;
- fresh attempt-scoped destination workspace/artifact-set identity;
- copied artifact count and total byte count;
- source-verification and destination-verification evidence identities;
- worker and implementation identities;
- closed staging disposition; and
- receipt contract version.

The receipt MUST NOT contain a private path. A successful disposition requires
verification of every and only manifest-declared regular file at both source
and destination. Links, path traversal, special files, undeclared files,
pre-existing destination collisions, count/size-limit violations, and digest
mismatches MUST fail closed.

The staging execution-evidence event identifies the resulting receipt reference;
the receipt MUST NOT identify that post-hoc event, which would create a
content-identity cycle. The receipt MAY safely identify the already-derived
plan, requirement, occurrence, attempt, and effect intents.

The runtime MUST durably retain the exact receipt reference and verify it against
the plan's requirement before it may admit the dependent effect's dispatch
authorization. The dependent effect intent identifies only the prior requirement;
the later dispatch authorization and execution evidence MUST identify the actual
receipt. The derivation is therefore acyclic:

```text
plan -> effect intents + receipt requirement
     -> staging authority/evidence -> actual receipt
     -> dependent dispatch authority/evidence
```

A staging exception or indeterminate write cannot be represented as a successful
receipt; it retains the occurrence reservation and enters staging reconciliation
before any restaging or dependent dispatch.

A staging receipt establishes a verified transfer relationship. It does not by
itself establish the semantic adequacy, scientific validity, or completeness of
the source or resulting calculation.

## Persistence and replay

Canonical history MUST retain compact identities and payload references, not
payload bodies, native files, credentials, or machine paths.

Parent and child histories MUST be independently verifiable and connected by
retained child-creation, child-instance, terminal-delivery, and parent-firing
evidence. A mutable projection MUST NOT manufacture or repair those links.

`WorkflowCpnBindingsCompleteReplayVerifier` is a future outer verifier. It is
not the bounded Slice A replay subject defined by
`projectkoios.workflow.runtime@0.1.0`, and this proposal does not expand Slice A
by implication. The outer verifier MUST first invoke and accept unchanged Slice
A identity-chain replay, which performs no artifact read or CPN execution, over
the exact event schema/segment owned by Slice A. Each subsequent event-schema
segment MUST be verified by its separately accepted later-slice verifier, and
the outer verifier MUST verify the predecessor/ordinal bridge between segments.

After successful Slice A verification, complete CPN-bindings replay MUST:

1. use the exact retained canonical flat definitions, control-record type
   definitions, value-model and expression-grammar profiles, CPN execution
   profiles, execution plans, and deployment-binding evidence rather than
   current registry entries;
2. resolve every required payload reference through a read-only immutable
   artifact boundary;
3. verify reference identity, color-binding agreement, payload byte size, and
   SHA-256 before decoding;
4. invoke only the exact retained schema-version codec and reject noncanonical
   or semantically invalid payloads;
5. reconstruct and verify the runtime safety state machine, including:
   - request retention and active-occurrence reservation ownership;
   - deterministic occurrence order and exact selected CPN binding;
   - child-create intent retention before child creation;
   - plan retention before any dispatch authorization;
   - bounded attempt and claim/lease identity where applicable;
   - exact attempt-bound authority before every worker call;
   - execution or ambiguity evidence before outcome processing;
   - reconciliation before any retry after ambiguity;
   - separately authorized cancellation and its observed result;
   - actual staging-receipt retention before dependent dispatch authority;
   - exact terminal classification and requirement selection;
   - primary and canonical ordered companion admission, retention phase,
     correlation, and delivery assembly before parent logical firing;
   - exact child terminal delivery before parent logical firing;
   - terminal parent commit before projection advancement; and
   - terminal resolution of every admitted child, attempt, cancellation, and
     ambiguity before quiescence;
6. reconstruct child-instance, primary terminal payload, companion-evidence,
   terminal-delivery, and parent-delivery correlations, including exact canonical
   mapper-input order;
7. replay pure CPN control-record validation, field projection, record
   construction, enablement, ordering, selection, external-output validation,
   and firing with the exact retained value model, grammar, validators,
   evaluator, and CPN execution profile, without provider, worker, artifact
   resolver, owner codec, domain constructor, callback, clock, filesystem, or
   calculator calls inside the CPN kernel; and
8. compare reconstructed markings, terminal outcomes, lifecycle state, and
   quiescence evidence with retained identities.

Payload resolution and decoding are a bounded outer preverification phase, not
Slice A replay and not CPN guard or firing behavior. A structural diagnostic MAY
omit owner payload resolution or full runtime-state reconstruction, but it MUST
be labeled incomplete and MUST NOT claim complete replay, semantic payload
verification, or safety-state verification.

Missing required runtime records, payloads, reference documents, CPN profiles,
unsupported codecs or schemas, changed child exports, plan-closure mismatches,
missing or ambiguous companion evidence, corrupt receipts, or unavailable
retained evidence MUST fail closed. Neither
Slice A nor the outer verifier may silently upgrade a schema, substitute a
current definition or child plan, repair history, or repeat an external effect.

## Cancellation, late delivery, and quiescence

A parent cancellation/finalization policy MUST identify the admitted child set
from retained history. After finalization begins, the runtime MUST reject new
child admission.

Every admitted child MUST reach one of:

- accepted quiescent terminal outcome;
- provider-confirmed cancellation followed by a definition-declared terminal
  outcome and evidence that no child process remains active; or
- a terminal reconciliation disposition that establishes either
  `CONFIRMED_NOT_APPLIED` with no later attempt admitted, or
  `CONFIRMED_APPLIED` with its retained result processed to a
  definition-declared terminal outcome and operational containment.

`STILL_AMBIGUOUS`, `EVIDENCE_INVALID`, `CONFIRMED_PARTIAL`, a merely requested
cancellation, or another partial/unresolved result is not terminal containment
and cannot satisfy this rule.

Late and duplicate deliveries or companions MAY be retained as evidence.
Acceptance MUST be idempotent by exact delivery and parent-occurrence identity.
A late companion MUST NOT mutate an already accepted delivery; a late delivery
MUST NOT recreate a consumed parent active token, create a second parent firing,
select another terminal outcome, or enable post-terminal domain work.

The runtime MAY emit parent quiescence evidence only when every admitted child
has one of the terminal outcomes above, every required terminal-delivery
assembly is either accepted exactly once or terminally reconciled without parent
firing, and no active claim, attempt, companion-production intent, delivery
assembly, cancellation, child process, `STILL_AMBIGUOUS`, `EVIDENCE_INVALID`,
`CONFIRMED_PARTIAL`, or other unresolved result remains. A child terminal commit
alone is insufficient when its classification requires companion evidence. A
reconciliation record is insufficient unless it establishes the permitted
terminal disposition. Quiescence does not imply domain success.

## Managed-project and provider ownership

Generic Workflow owns:

- generic reference and binding records;
- plan-closure and deployment-link validation;
- terminal-delivery requirements and canonical companion-input ordering;
- net-instance, occurrence, attempt, delivery, and quiescence identities;
- reservation, authority admission, persistence, replay, cancellation
  coordination, and reconciliation semantics; and
- enforcement of staging-receipt prerequisites declared by a plan.

A child/provider owner owns:

- the authoritative child source definition and deterministic export;
- provider-native request, job, result, saved-state, and manifest schemas;
- source and destination byte verification;
- native job and artifact identities; and
- mechanical result and provider semantic-normalization evidence.

A managed project owns:

- parent scientific topology;
- domain payload schemas and codecs;
- scientific role, threshold, candidate, and acceptance policy;
- mapping from provider evidence to accepted project records; and
- final domain disposition.

No owner may duplicate another owner's topology or reinterpret another owner's
payload without an explicit versioned adapter.

## Consumer-profile reconciliation summary

This table records how the owner proposal treats the Si-VC requirements. It is
not contract acceptance or implementation evidence.

| Consumer requirement | Treatment in this proposal |
|---|---|
| One runtime-neutral canonical CPN | Adopted as one flat canonical CPN per net instance |
| Existing typed source records and field guards | Adopted through bounded generic control records plus closed field-projection and record-construction expressions; no live domain objects or topology-visible token splitting |
| Definition closure binds payloads and children | Adopted as `WorkflowExecutionPlanIdentity`; flat CPN identity remains narrower |
| Exact six-field `DomainPayloadReference` | Adopted without adding envelope fields |
| Strict owner codecs and canonical JSON | Adopted as pure encoding/metadata plus outer retention and pure reference assembly, all outside the CPN kernel |
| Guards never parse artifacts | Adopted without exception |
| Reference authoritative child without copied topology | Adopted through separately compiled child export and plan references |
| Durable hierarchical child instance | Adopted as runtime nesting, not live hierarchical CPN semantics |
| Child fan-out | Deferred; v0.1 requires exactly one child at canonical ordinal `0` per parent occurrence |
| Fresh loop instance versus same-occurrence retry | Adopted with distinct occurrence and attempt identities |
| Parent substitution transition | Refined: selection/reservation launches; logical firing commits after terminal delivery |
| Runtime identity ordering | Refined to request before occurrence so content derivation is acyclic |
| Provider candidate versus project acceptance | Preserved as distinct owner payload schemas |
| Terminal payload plus separately retained provider evidence | Adopted through classification-specific terminal-delivery and companion-evidence requirements without changing child topology |
| SCF-to-NSCF staging receipt barrier | Adopted and strengthened with a distinct staging effect intent and evidence |
| Persistence and complete replay | Adopted as a future outer verifier that first accepts unchanged Slice A replay, then verifies payloads, runtime safety state, and pure CPN replay |
| Cancellation, late delivery, reconciliation, and quiescence | Adopted as runtime-owned semantics |
| Concrete APIs and implementation | Still blocked and outside this proposal's authorization |

## Informative Si-VC stress-case mapping

The proposed Si-VC consumer profile exercises this generic contract as follows:

| Generic concept | Si-VC role |
|---|---|
| Parent flat CPN | 56-place/55-transition `si_vc_component_locality` net |
| Nested parent transition | `execute_scf_child` |
| Child export | simulations-owned `dft_pw_scf` source with 12 places and 8 transitions |
| Primary child terminal payload | Successful SCF terminal-outcome reference from the unchanged terminal port |
| Candidate provider companion | Separately retained post-terminal QE saved-state candidate after successful execution and verified manifest |
| Managed-project acceptance payload | accepted SCF parent binding unchanged candidate handoff to role, coordinate, normalized evidence, policy, and acceptance occurrence |
| Staging receipt | fresh attempt-scoped SCF-to-NSCF verified copy receipt |
| Dependent protected effect | exact NSCF calculator occurrence and attempt |
| Separate semantic gate | post-success NSCF QEXSD/source-frame qualification |

The authoritative simulations child currently uses SNAKES and does not yet emit
the required saved-state companion. Conformance therefore requires an
owner-controlled canonical child exporter/adapter, a success-classification
terminal-delivery requirement, and provider schema work; the companion remains
runtime evidence and the parent MUST NOT copy or modify the
twelve-place/eight-transition topology. This table is
an architecture stress case, not a Generic Workflow dependency on Si-VC or an
execution authorization.

## Required conformance vectors

An implementation claiming this contract MUST provide synthetic, payload-free
fixtures for at least:

1. canonical six-field payload-reference encode/decode and stable reference
   identity;
2. a pure owner codec producing bytes/metadata, an outer artifact operation
   supplying the retained artifact identity, and a pure assembler computing
   digest and size without codec store access or locator fabrication;
3. rejection of duplicate, unknown, missing, wrongly typed, oversized,
   noncanonical, path-bearing, digest-mismatched, and byte-size-mismatched
   references or payloads;
4. changed payload bytes, schema, media type, digest, byte size, or artifact
   identity changing the reference identity, and a changed codec/owner changing
   the execution-plan identity;
5. payload-token admission and replay rejecting wrong schema, media type,
   owner/codec resolution, maximum size, payload digest, payload byte count,
   per-complete-marking reference-count overflow, missing required token
   identity, or duplicate required token identity;
6. a guard unable to resolve, decode, or inspect payload bytes;
7. each semantic flat-definition mutation changing the canonical-definition
   digest and execution-plan identity even when its nominal definition identity
   is unchanged;
8. each value-model, definition/marking/binding/result representation,
   definition-validator, marking-validator, evaluator, enabler, ordering,
   selector, external-output-validator, and firer profile mutation changing the
   CPN execution-profile and execution-plan identities;
9. plan identity changing when a payload-color binding changes while the flat
   CPN definition identity remains unchanged;
10. child export validation against an independently stated flat child plan;
11. parent plan containing the exact child export/binding but no copied child
    place, transition, arc, guard, or inscription definitions;
12. stable child topology across different run subjects and distinct initial
    markings;
13. v0.1 compile/link rejection of child cardinality other than one or canonical
    child ordinal other than signed integer `0`;
14. fresh child instance for a later loop occurrence and no fresh child instance
    for an ambiguous retry of the same occurrence;
15. atomic retention of child-creation intent before child creation;
16. lost child-creation acknowledgement routing to reconciliation without a
    duplicate child instance;
17. wrong parent, child, definition, port, occurrence, attempt, history-head,
    mapper, or terminal-classification delivery failing closed;
18. child terminal success, known failure, and confirmed cancellation mapping
    only through declared terminal ports and normal parent firing;
19. infrastructure failure and ambiguity producing no fabricated parent firing;
20. every protected child effect requiring distinct exact-occurrence authority;
21. authority expiry or revocation blocking a later attempt;
22. cancellation/success races producing one deterministic retained terminal
    mapping;
23. late and duplicate delivery producing no second parent firing or terminal
    token;
24. quiescence withheld for active claims, attempts, cancellations, child
    processes, `STILL_AMBIGUOUS`, `EVIDENCE_INVALID`, `CONFIRMED_PARTIAL`, or
    any other unresolved state;
25. source-manifest verification, fresh-workspace copy, destination
    verification, and actual receipt retention before dependent dispatch;
26. a plan and dependent effect intent containing only the receipt-requirement
    identity, with the actual receipt first entering staging evidence and later
    dependent dispatch authority/evidence without a content-identity cycle;
27. one-file source, destination, manifest, handoff, receipt, plan, CPN profile,
    canonical definition, export, or event tamper failing closed;
28. the outer complete-replay verifier first accepting unchanged Slice A and
    each later-slice segment verifier plus continuous predecessor/ordinal bridges
    before reading artifacts or executing pure CPN replay;
29. complete replay reconstructing reservation, plan, attempt, authority,
    ambiguity, reconciliation, cancellation, receipt-barrier, child-delivery,
    terminal-commit, and quiescence semantics plus exact parent/child markings;
30. complete replay making no provider, calculator, worker-effect, or other
    external effect call during pure CPN replay;
31. runtime events and diagnostics containing no payload bodies, credentials,
    private paths, or protected excerpts; and
32. software conformance reported separately from scientific validation,
    uncertainty quantification, domain acceptance, publication, and execution
    authority;
33. every admitted terminal classification having exactly one closed delivery
    requirement, including an explicit empty companion tuple for a
    no-companion classification;
34. a changed terminal-delivery or companion requirement changing child export,
    child plan, and enclosing parent-plan identities without changing or copying
    child topology;
35. rejection of noncontiguous requirement ordinals, invalid minimum/maximum or
    total cardinality, duplicate reference use, and representation-bound
    overflow;
36. canonical mapper inputs containing the primary reference first, then
    requirements by ordinal, then references by lexical reference identity;
37. missing, excess, duplicate, wrong-role, wrong-schema, wrong-codec,
    wrong-media-type, wrong-phase, stale, cross-child, noncanonical-order, or
    correlation-failing companion evidence producing no delivery or parent
    firing, while a known-failure classification neither requires nor fabricates
    a success-only companion;
38. post-terminal companion retention failure or ambiguity preserving the child
    terminal commit while retaining the parent reservation and routing to
    reconciliation;
39. a pure output mapper receiving only already-admitted primary and companion
    inputs and making no resolver, codec, store, provider, filesystem, network,
    clock, worker, or kernel call;
40. delivery identity changing with any primary, companion, requirement,
    terminal-head, correlation, mapper, child, or parent-occurrence input while
    excluding the future parent firing identity; and
41. complete replay reconstructing companion admission, production phase,
    canonical input order, correlation, delivery assembly, ambiguity, and
    quiescence without repeating a protected effect;
42. canonical control-record encode/decode and marking admission at every type-
    definition, field, record-node, record-depth, expression-node, expression-
    depth, string, sequence, and byte bound, plus rejection one unit beyond each
    applicable bound;
43. rejection of duplicate, missing, unknown, wrongly typed, noncanonical,
    cyclic, open, wrong-record-type, and non-lexically ordered control-record
    fields and of cyclic or over-depth record-type graphs;
44. every record-type, color/type admission, field kind, field order, projection
    path, constructor field expression, value-model bound, grammar, validator,
    evaluator, external-output validator, and owner mapping-descriptor mutation
    changing the canonical-definition, execution-profile, or execution-plan
    identity to which it contributes;
45. field projection preserving matching evaluation/task identities and
    rejecting unrelated identities, and record construction preserving exact
    registration, submission, analysis, success, and known-failure outputs for
    the unchanged simulations SCF twelve-place/eight-transition fixture;
46. SCF parity retaining one control-record token for each source action, event,
    request, analyzed output, and terminal outcome without adding fact places,
    splitting one source token, moving a source guard into admission policy, or
    invoking a provider-native class or constructor inside the kernel;
47. complete replay reconstructing control records, projections, constructors,
    and successor markings with the exact retained type definitions, value
    representation, grammar, validators, evaluator, and mapping descriptors,
    while rejecting substitution of current defaults; and
48. static dependency and adversarial expression fixtures proving that no
    callable, import, source expression, reflection, arbitrary attribute,
    subscript, payload decoder, artifact resolver, domain object, or hidden
    callback can enter record validation, guard evaluation, construction,
    enablement, or firing.

Cross-repository conformance MUST identify exact contract, specification,
implementation, child-provider, and managed-project revisions plus fixture and
validation-result identities.

## Acceptance gates

This proposal is ready for acceptance review only when:

- workflow-owner review finds the flat-kernel, execution-plan, runtime, and
  persistence boundaries internally consistent;
- at least one child provider reviews and supplies a complete export/schema
  fixture without copying topology into a consumer;
- at least one managed project reviews and supplies parent binding, payload,
  terminal-correlation, and classification-specific companion fixtures;
- canonical flat-definition and every CPN execution-profile mutation vector,
  including control-record type, bound, field, projection, constructor, grammar,
  validator, evaluator, and mapping-descriptor mutations, change the execution-
  plan identity as specified;
- canonical payload-reference, pure codec/retention/assembly, and color-binding
  admission vectors pass in independent owner and consumer implementations;
- a later accepted runtime slice retains the plan, attempt, authority, effect,
  reconciliation, cancellation, receipt, terminal-commit, and quiescence records
  required by the outer complete-replay verifier;
- the unchanged simulations SCF twelve-place/eight-transition fixture passes
  field-guard, constructor-output, mismatched-identity, success, and known-failure
  parity without token splitting, topology change, or a domain callback;
- parent/child crash, ambiguity, companion-retention, cancellation,
  late-delivery, and replay vectors pass without duplicate effects, delivery
  mutation, or fabricated firing;
- artifact resolver and staging-receipt fixtures preserve privacy and exact-byte
  provenance;
- authority admission remains separate from structural enablement and child
  creation;
- dependency-direction checks keep the generic kernel and core independent of
  managed-project and provider packages; and
- implementation, migration, merge, and release remain separately authorized.

Passing these gates does not authorize protected execution or establish
scientific correctness.

## Deferred decisions

This contract does not select:

- final Python modules or public import paths;
- public wire compatibility duration;
- artifact-store technology or locator-sealing mechanism;
- the authority issuer, signature, expiry, or revocation service;
- worker pull versus authenticated control-plane push;
- queue, claim, lease, or process-supervisor implementation;
- whether operational lifecycle state uses one expanded flat net or a correlated
  companion operational CPN, provided the nested-route protocol remains
  observable and authoritative;
- database, backup, archival, or deployment technology;
- child fan-out greater than one, including set retention, per-ordinal launch,
  aggregation, cancellation, and terminal-set semantics;
- compensation policy for partially applied effects;
- provider or consumer migration order; or
- release and rollback procedures.

These choices require separate reviewed records and MUST NOT be inferred from a
consumer profile.

## Stop conditions

Stop before implementation or execution if:

- an execution plan would omit the exact canonical flat-definition digest or any
  required CPN execution-profile identity;
- a parent or deployment artifact would copy child topology;
- a raw JSON body, arbitrary mapping, native object, credential, or machine path
  would enter a CPN token or canonical runtime event;
- a codec would fabricate or retrieve an artifact identity, or an artifact store
  would be hidden inside a pure codec operation;
- a payload-reference token could enter a marking without exact color-binding,
  payload-byte, owner, codec, per-complete-marking count, and required individual
  token-identity admission checks;
- a v0.1 hierarchical binding would admit child cardinality other than one or a
  child ordinal other than signed integer `0`;
- a guard would fetch or decode an external payload, traverse anything other
  than an admitted bounded control record, or invoke an arbitrary attribute,
  subscript, callable, import, source expression, reflection facility, owner
  object, or domain constructor;
- a control record would be open, cyclic, unbounded, schema-free, contain a
  native domain object or payload body, or bypass its exact type definition,
  color/type admission, canonical decoding, or validator;
- an exporter would preserve field guards by splitting one source token into
  several topology-visible tokens, adding places/transitions, or moving the
  source guard into outer admission policy rather than using the closed
  projection/construction grammar;
- child creation could occur before durable unique-instance retention;
- ambiguous child creation or effect execution could trigger automatic
  recreation or redispatch;
- a parent transition could fire before exact child terminal correlation or
  before every classification-required companion is retained, admitted, ordered,
  and correlated;
- a companion could be treated as a child terminal token, mutate child topology
  or marking, satisfy two requirement occurrences, or enter a mapper that hides
  resolution, decoding, provider, filesystem, network, clock, or store access;
- child or parent protected effects could run without exact attempt-bound
  authority;
- a staging receipt could be created without source and destination
  verification, admitted after dependent dispatch, or embedded as a future
  identity inside the plan or dependent effect intent;
- cancellation, timeout, lease expiry, or worker loss could be treated as proof
  of non-execution;
- Slice A replay could be redefined by implication, or the outer complete replay
  verifier could call providers or substitute current definitions/profiles for
  retained ones;
- quiescence could be reported with an active child, claim, attempt,
  companion-production intent, delivery assembly, cancellation, partial
  application, invalid evidence, or unresolved ambiguity;
  or
- implementation, dependency change, provider migration, protected execution,
  commit, merge, release, or publication would begin without its separately
  required authorization.
