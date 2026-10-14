# Bounded CPN control records and expressions

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Bounded generic control records

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

## Closed field projection and record construction

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

## No hidden semantic callbacks

The generic CPN kernel MUST evaluate only its closed admitted value kinds,
guards, inscriptions, markings, and bindings. Kernel enablement or firing MUST
NOT call an artifact store, payload codec, domain object, registry, provider,
worker, clock, network service, or filesystem.

Facts needed by a guard MUST already be explicit scalar/status values or fields
of an admitted bounded control-record token in the marking. A field projection
MUST traverse only that immutable admitted control record. A guard MUST NOT
fetch a referenced payload, inspect payload fields, invoke an owner object, or
call an arbitrary callback.
