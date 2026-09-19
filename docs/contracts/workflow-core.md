# Petri-independent workflow core contract

## Contract metadata

| Field | Value |
|---|---|
| Contract ID | `projectkoios.workflow.core` |
| Target version | `0.2.0` |
| Status | Proposed |
| Change classification | Breaking normative revision of the unaccepted `0.1.0` proposal |
| Proposal lineage | Replaces the proposed draft at `a033c22c7f0eadd5e776d2969e541ff0af217f50`; no accepted baseline is superseded |
| Specification revision | Git commit containing this document |
| Owner | `projectkoios-workflow` |
| Acceptance authority | Project Koios operator after workflow-owner review and review by one named prospective consumer owner |
| Architecture record | [`ADR20260918`](https://github.com/eragasa/projectkoios/blob/main/docs/adr.20260918.workflow-kernel-transfer.md) |
| Task | [`WORKFLOW-CORE-01`](https://github.com/eragasa/projectkoios-workflow/issues/1) |
| Predecessor | None registered |
| Supersedes | None while proposed |
| Dependencies | No accepted cross-repository contract dependencies |
| Prospective consumers | Workflow runtime, engine adapters, and managed-project adapters; none accepted yet |
| Implementation bindings | The colored-Petri-net shadow is backend evidence, not a core implementation |
| Compatibility | Breaking relative to the unaccepted `0.1.0` proposal; acceptance still requires one bounded feasibility spike and named prospective-consumer review and grants no adapter or wire compatibility |
| Effective baseline | None while proposed |

## Status and authority

This contract is proposed under
[`WORKFLOW-CORE-01`](https://github.com/eragasa/projectkoios-workflow/issues/1).
It does not authorize implementation, production transfer, consumer adoption,
migration, release, deprecation, or source removal.

The current owner task authorizes contract analysis and review only. Executable
conformance vectors or a disposable feasibility spike require separate bounded
authorization recorded before that work begins. A spike is non-production
evidence and cannot become the authoritative implementation by implication.
Core-contract acceptance, production implementation, adapter implementation,
and every later transfer decision remain separate actions.

## Purpose

The workflow core defines a pure, bounded transition protocol for describing
and auditing workflow state changes without depending on a colored-Petri-net
representation, scheduler, persistence engine, user interface, external
executor, or scientific application.

The existing colored-Petri-net package remains a non-authoritative backend
shadow. The core is not a renamed copy of `ksdft2effmass.workflows.model`, and
the shadow kernel is not changed merely to fit this proposal.

## Normative scope and terminology

The sections from **Normative data model** through **Serialization boundary**
are normative for `projectkoios.workflow.core` version `0.2.0`. The capitalized
terms **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**,
**SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** have the meanings
specified by Project Koios contract governance. Examples, rationale, status,
acceptance planning, and deferred decisions are informative.

The conformance subjects are:

- a core evaluator;
- a core validator;
- a replay validator;
- a provisional boundary parser or serializer; and
- an adapter claiming to supply results to the core.

Every conformance claim MUST identify the contract ID and version, exact
specification commit, implementation commit, conformance-subject kind, fixture
or adapter-evidence identity, and validation result. Passing conformance tests
MUST NOT be represented as architecture acceptance, authorization, consumer
compatibility, scientific validity, or production-transfer evidence.

In this contract:

- **semantic equality** means field-by-field equality under the typed model in
  this document, including ordered-list order and typed-identifier nominality;
- **structural validation** means validation of types, bounds, exact bindings,
  and permitted values, not authentication or policy authorization;
- **outer boundary** means a separately owned parser, authentication or policy
  service, runtime, persistence layer, or adapter caller outside the pure core;
- **prior run** means the immutable run record supplied to one evaluation; and
- **successor run** means a new immutable run record produced only by an
  `APPLIED` outcome.

## Normative data model

### Primitive values and bounds

A conforming implementation MUST enforce these limits before constructing core
records:

| Value | Requirement |
|---|---|
| One encoded input document | At most 1,048,576 bytes before parsing |
| Contract version | Exactly `0.2.0` for this contract version |
| `AsciiToken` | 1–128 ASCII bytes matching `[a-z][a-z0-9._-]{0,127}` |
| `VersionToken` | 1–64 ASCII bytes matching `[0-9][0-9A-Za-z.+-]{0,63}` |
| `ContractId` | 3–128 lowercase ASCII bytes matching `[a-z][a-z0-9_-]*(\.[a-z][a-z0-9_-]*)+` |
| `CanonicalizationId` | One `ContractId` |
| Identity domain | Lowercase ASCII matching `[a-z][a-z0-9._-]{0,63}` |
| Identity value | 1–256 ASCII bytes matching `[A-Za-z0-9][A-Za-z0-9._:@/+~-]{0,255}` |
| Opaque locator | At most 2,048 printable ASCII bytes (`0x20..0x7e`); never dereferenced by the core |
| One ordered reference list | At most 128 entries |
| Findings in one evaluation | At most 64 entries |
| Audit events in one outcome | At most 7 entries under the exact construction rule |
| Revision | Integer in `0..9_223_372_036_854_775_807`; booleans are not integers |
| Embedded payload | Prohibited; references and digests are used instead |

A parser MUST reject unknown fields, duplicate fields, duplicate typed
identities in one list, invalid UTF-8 or non-ASCII normative text, out-of-range values, and oversized
input. It MUST NOT truncate, repair, normalize a control character away, or
partially construct a record after failure. An implementation that imposes a
smaller accepted bound does not conform to `0.2.0` for inputs between that bound
and the contract maximum.

If parsing and preconstruction validation cannot construct a complete valid
`EvaluationInputIdentity`, it returns an `InputRejection` containing exactly the
ordered stage 1 and stage 2 findings plus the stage 255 limit marker when
required by the finding-bound rule, and no `OutcomeId`, successor, or audit
events. An `InputRejection` is boundary
validation evidence, not a `TransitionOutcome`; this contract assigns it no
durable public identity. Normal transition evaluation begins only after the
bounded records required for `EvaluationInputIdentity` exist.

### Typed nominal identities

Every non-structural typed identity is a record containing exactly `domain` and
`value` fields constrained by the primitive table. Equality is field-by-field;
ordering is domain and then value by ASCII code point. Unknown or additional
identity fields are invalid.

`DefinitionId`, `RunId`, `SnapshotId`, `RequestId`, `ArtifactId`,
`DecisionId`, `AuthorityVerdictId`, `AdapterResultId`, `ReferenceId`, and
`ProducerId` are nominally distinct even when their domain and value strings
match.

A run and request use stable logical identities. A `RunId` MUST remain unchanged
when the run revision, snapshot, status, or references change. A `RequestId`
MUST be unique within its `ProducerRef`. The structural pair
`(request_producer, RequestId)` is the `IdempotencyKey` for one proposed
transition. Core conformance MUST NOT infer a logical identity from mutable
record content.

Structural evaluation identities are defined after `EvaluationContext` because
they include every bounded outcome-determining input. Structural identities
MUST NOT be serialized into one public string until a later wire contract
defines that encoding.

### Content digest reference

Immutable definitions, snapshots, requests, artifacts, authority verdicts,
and adapter results MUST carry a `ContentDigest` containing exactly:

- algorithm value `sha256`;
- 64-character lowercase hexadecimal digest value;
- `CanonicalizationId`; and
- `VersionToken` canonicalization version.

The producer owns the referenced bytes and canonicalization rule. For an
authority verdict or adapter result, the digest identifies the producer-owned
source-evidence payload; it does not recursively cover the core wrapper or its
own digest field. The core MUST compare the complete `ContentDigest` value
exactly but MUST NOT claim to recompute it unless the canonicalization is
implemented by a separately identified boundary conformance subject. Equal
digest strings under different canonicalization identities or versions are not
equal evidence.

### Common producer and external references

A `ProducerRef` MUST contain exactly a `ProducerId` and `VersionToken`.
Producer equality is field-by-field equality of both values. Producer ordering
is `ProducerId` domain and value by ASCII code point, then producer version by
ASCII code point. A list described as an
accepted-producer list MUST be sorted in this order and contain no duplicates.

An `ExternalRef` MUST contain exactly:

- reference-kind `AsciiToken`;
- `ReferenceId`;
- `ProducerRef`;
- reference `VersionToken`; and
- OPTIONAL `ContentDigest`.

The permitted reference-kind tokens in `0.2.0` are `subject`, `actor`, `scope`,
`provenance`, `policy_observation`, `evidence`, and `input`. Equality is
field-by-field equality, including the complete OPTIONAL digest. A field that
requires one reference kind MUST reject every other kind. An ordered list of
references compares in list order; an unordered reference set is not part of
this contract.

A reason code is an `AsciiToken`. A reason-code list is ordered,
contains no duplicates, and is limited by the ordered-reference-list bound.
Display prose is outside the normative core record and MUST NOT affect identity,
validation, ordering, or outcome kind.

### Evaluation context and structural evaluation identities

An `EvaluationContext` MUST contain exactly:

- core contract version;
- a non-empty authority-producer list of accepted `ProducerRef` values;
- a non-empty ordered list of accepted policy `(ContractId, VersionToken)` pairs;
- one required `ExternalRef` whose kind is `policy_observation`;
- a separate non-empty adapter-producer list of accepted `ProducerRef` values;
  and
- a non-empty ordered list of accepted adapter `(ContractId, VersionToken)`
  pairs.

The authority and adapter producer lists are separate and MUST NOT be combined
or substituted for each other. Accepted policy and adapter pairs MUST be sorted by
`ContractId` and then `VersionToken` using ASCII code-point order and contain no
duplicates. `EvaluationContext` equality is field-by-field equality.

`EvaluationContextId` is the typed structural tuple of all `EvaluationContext`
fields in the order listed above. `EvaluationInputIdentity` is the typed
structural tuple containing, in order:

1. complete `TransitionRequest`, including its `IdempotencyKey`, request digest,
   and embedded `AuthorityVerdict`;
2. complete prior `WorkflowRun`;
3. complete OPTIONAL `AdapterResult`, represented by an explicit absence marker
   when no adapter result is supplied;
4. complete `EvaluationContext`; and
5. core contract version.

Every component is bounded elsewhere in this contract. `OutcomeId` is the typed
structural pair `(EvaluationInputIdentity, "evaluation")`. `AuditEventId` is
the typed structural triple `(OutcomeId, zero_based_ordinal, event_kind)`.
`ReplayRejectionId` is the typed structural triple
`(retained_EvaluationInputIdentity, candidate_EvaluationInputIdentity,
"changed_input")`. These identities compare recursively in tuple order and
MUST NOT be flattened into a public string before a wire contract defines that
encoding.

`ReplayRejectionId` is distinct from `OutcomeId`. Any change to a request,
prior run, verdict, adapter result, policy observation, allowlist, or accepted
version changes the corresponding evaluation identity.

### Definition reference

A `DefinitionRef` MUST contain a `DefinitionId`, immutable definition
`VersionToken`, `ContentDigest`, `ProducerRef`, and core contract version. Equality is
field-by-field equality. It MUST NOT contain executable code, a database handle,
Petri marking, or UI configuration. Engine-specific definition identity belongs
in adapter evidence.

### Snapshot reference

A `SnapshotRef` MUST contain a `SnapshotId`, state-kind `AsciiToken`, `ContentDigest`,
`ProducerRef`, and an ordered list of `ExternalRef` values whose kind is
`evidence`. Equality is field-by-field equality. It is immutable. The core MUST
NOT interpret a Petri marking or application payload as its universal state
model.

### Workflow run

A `WorkflowRun` MUST contain:

- stable `RunId`;
- `DefinitionRef`;
- one `ExternalRef` whose kind is `subject`, without an imported
  subject-domain object;
- current `SnapshotRef`;
- revision;
- status;
- OPTIONAL parent or predecessor `RunId`;
- ordered `ArtifactRef` and `DecisionRef` values; and
- core contract version.

The only run statuses are `ACTIVE`, `SUCCEEDED`, `FAILED`, and `CANCELLED`.
`SUCCEEDED`, `FAILED`, and `CANCELLED` are terminal. A run record is immutable
and does not own the subject, artifacts, decisions, or external processes that
it references.

### Artifact and decision references

An `ArtifactRef` MUST contain an `ArtifactId`, kind `AsciiToken`, `ContentDigest`,
`ProducerRef`, one `ExternalRef` whose kind is `provenance`, role `AsciiToken`,
and OPTIONAL opaque locator. A `DecisionRef` MUST contain a `DecisionId`,
decision-kind `AsciiToken`, one `ExternalRef` whose kind is `subject`, an ordered non-empty list
of `ExternalRef` values whose kind is `scope`, one `ExternalRef` whose kind is
`actor` for the asserted authority, outcome `AsciiToken`, `ContentDigest`, and
decision `VersionToken`. Equality for both records is field-by-field equality.

The core MUST treat an artifact locator as opaque data and MUST NOT open a file,
resolve a path, fetch a URL, use embedded credentials, or reinterpret artifact
content. Any consuming boundary MUST enforce its own allowed schemes, root
confinement, credential prohibition, privacy classification, and
declassification policy before dereferencing a locator.

Generated, observed, technically validated, accepted, and published artifacts
MUST remain distinguishable. Referencing an artifact or decision MUST NOT grant
acceptance, publication authority, or scientific validity.

### Authority verdict

An `AuthorityVerdict` MUST be immutable and contain:

- `AuthorityVerdictId` and source-evidence `ContentDigest`;
- verdict `AUTHORIZED`, `DENIED`, or `INDETERMINATE`;
- exact `IdempotencyKey` and request `ContentDigest`;
- exact `RunId`, `ExternalRef` values of kind `subject` and `actor`, operation
  `AsciiToken`, and ordered non-empty list of `ExternalRef` values whose kind is
  `scope`;
- policy `ContractId` and policy `VersionToken`;
- one `ExternalRef` whose kind is `policy_observation` and is supplied to this
  evaluation;
- `ProducerRef` whose authenticated identity is asserted by the outer boundary;
- bounded ordered reason codes; and
- ordered `ExternalRef` values whose kind is `evidence`, including references
  to any time evidence used by the policy producer.

The pure core MUST NOT authenticate the producer, read a clock, discover
revocation, evaluate policy, or infer scope. The outer policy boundary owns
those actions. The core MUST require verdict idempotency key and request digest
to equal the request, verdict run and subject to equal the prior run, verdict
actor and operation to equal the request, and verdict producer, policy pair,
and policy observation to match the authority fields of `EvaluationContext`.
Only an exactly bound `AUTHORIZED` verdict may proceed to adapter-result
validation. `DENIED` or `INDETERMINATE` produces `BLOCKED`. An absent or
structurally malformed mandatory verdict is a stage 1 or stage 2
`InputRejection`; only a structurally valid but mismatched or unaccepted verdict
reaches stage 5 and produces `INVALID`.

The `EvaluationContext` supplies the separate authority-producer list, accepted
policy pairs, and required policy-observation reference. The verdict's single
policy pair MUST be an exact member of the accepted policy-pair list. Matching
these values is structural validation; it MUST NOT be represented as
cryptographic authentication or the core granting authority.

### Transition request

A `TransitionRequest` MUST contain:

- unique `RequestId`, request `ProducerRef`, and source-evidence
  `ContentDigest` covering the producer-owned request payload while excluding
  both the digest field and the subsequently issued `AuthorityVerdict`;
- `RunId`, expected revision, and complete expected `SnapshotRef`;
- operation `AsciiToken`;
- ordered `ExternalRef` values whose kind is `input` and ordered
  `ArtifactRef` values;
- one `ExternalRef` whose kind is `actor`;
- exactly one complete `AuthorityVerdict`; and
- core contract version.

A request MUST NOT contain executable code. A request is not authorization.
Idempotency identity is never optional for a state-changing request.

### Adapter result

The request digest is therefore available before policy evaluation and cannot
be self-referential. The complete `IdempotencyKey` and request digest MUST match
the embedded verdict.

An `AdapterResult` MUST be immutable and contain:

- `AdapterResultId` and source-evidence `ContentDigest`;
- adapter `ContractId` and adapter `VersionToken`;
- `ProducerRef` whose authenticated identity is asserted by the outer boundary;
- exact `IdempotencyKey`, request `ContentDigest`, `RunId`, expected revision,
  complete prior `SnapshotRef`, complete `DefinitionRef`, operation `AsciiToken`, and
  core contract version;
- result kind `SUCCESSOR`, `NOT_ENABLED`, `BLOCKED`, or
  `INFRASTRUCTURE_FAILURE`;
- OPTIONAL successor `SnapshotRef` and successor run status;
- bounded ordered reason codes; and
- ordered `ExternalRef` values whose kind is `evidence`.

`SUCCESSOR` MUST contain one successor snapshot and permitted successor status.
Every other result kind MUST NOT contain a successor. The `EvaluationContext`
supplies the separate adapter-producer list and accepted adapter contract
pairs. The core MUST require adapter idempotency key, request digest, run,
revision, complete prior snapshot, complete definition, operation, and contract
version to equal the request and prior run as applicable, and adapter producer
and contract pair to match the adapter fields of `EvaluationContext`. It MUST
reject missing, stale, wrong-version, wrong-producer, wrong-request-producer,
wrong-request-digest, or incomplete prior-state bindings. It MUST NOT
authenticate the producer or execute the adapter.

### Transition outcome and audit events

A `TransitionOutcome` MUST contain exactly its deterministic `OutcomeId`,
complete `EvaluationInputIdentity`, result kind, ordered findings, ordered audit
events constructed below, and OPTIONAL successor run. The only result kinds are:

- `APPLIED`;
- `INVALID`;
- `NOT_ENABLED`;
- `CONFLICT`;
- `BLOCKED`; and
- `INFRASTRUCTURE_FAILURE`.

Only `APPLIED` contains a successor run. Every non-applied result MUST preserve
the prior run without manufacturing a successor snapshot or revision.
Infrastructure failure MUST NOT be encoded as business rejection, policy
denial, scientific decision, or human decision.

Audit events are constructed exactly as follows:

1. For each reached domain-evaluation stage from 3 through 7, append one event with
   structural `AuditEventId`, `OutcomeId`, next zero-based ordinal, event kind
   `validation_stage`, that numeric stage key, and the ordered slice of outcome
   findings from that stage. The slice may be empty.
2. If `finding_limit_exceeded` exists, append one event with event kind
   `finding_limit`, stage key 255, and only that finding.
3. Append one final event with event kind `outcome_constructed`, no stage key,
   an empty finding list, and the outcome result kind.

No other audit event is generated by `0.2.0`. Audit order is list order and
ascending ordinal. The final event is therefore ordinal `reached_stage_count`
or `reached_stage_count + 1` when the finding-limit event exists. Audit events
are evidence records; the core does not choose an event store.

## Normative transition protocol

### Allowed state transitions

An `APPLIED` outcome MUST construct the successor `WorkflowRun` by changing
exactly three prior-run fields: revision increments by one, current
`SnapshotRef` becomes the validated adapter successor snapshot, and status
becomes the validated adapter successor status. It MUST preserve the complete
`RunId`, `DefinitionRef`, subject `ExternalRef`, parent/predecessor `RunId`,
ordered artifact references, ordered decision references, and core contract
version field by field. Version `0.2.0` does not append, remove, or replace run
artifacts or decisions during this transition operation.

The only permitted status transitions are:

| Prior status | Successor status |
|---|---|
| `ACTIVE` | `ACTIVE`, `SUCCEEDED`, `FAILED`, or `CANCELLED` |
| `SUCCEEDED` | none |
| `FAILED` | none |
| `CANCELLED` | none |

An evaluation of a terminal run MUST produce `CONFLICT` with `terminal_run`.
An `ACTIVE` run at maximum revision MUST produce `CONFLICT` with
`revision_exhausted` at stage 4 before authority or adapter validation. A caller
cannot reopen a terminal run or advance an exhausted run under this contract.
Creation of a new run uses a new `RunId` and is outside this transition
operation.

### Validation order and stable findings

A `FieldPath` is an ordered tuple of path segments. A segment is either a field
name matching `[a-z][a-z0-9_]{0,63}` or a non-negative list index no larger than
127. It is a structural value, not a dot-separated or JSON Pointer string.

A `Finding` MUST contain exactly a numeric stage key, reason code, `FieldPath`,
and OPTIONAL related typed identity. Display prose is not a finding field.

A conforming evaluator MUST execute these canonical stages in numeric order and
MUST NOT consult an adapter result after an earlier stage determines that the
request cannot proceed:

| Key | Stage |
|---:|---|
| 1 | contract version, encoded size, UTF-8/ASCII, primitive type, field, and bound preconstruction validation |
| 2 | typed identity, duplicate, and structural-reference preconstruction validation |
| 3 | run, definition, and complete snapshot consistency |
| 4 | terminal state, expected revision, idempotency-key, and retained-history checks |
| 5 | authority-verdict binding and verdict checks |
| 6 | adapter-result producer, version, and exact-binding checks |
| 7 | adapter-result and successor-transition consistency |
| 255 | internal finding-bound marker only |

Finding order is the tuple `(stage_key, code, field_path, related_identity)`.
Comparison is defined as follows:

1. stage keys compare numerically;
2. codes compare by ASCII code point;
3. field paths compare segment by segment, with field-name segments before
   index segments, field names by ASCII code point, indices numerically, and a
   shorter equal-prefix path first; and
4. a missing related identity sorts before a present identity. Present
   identities MUST be one non-structural typed identity and sort by this fixed
   type rank, then identity domain and value by ASCII code point:
   `ProducerId`, `DefinitionId`, `RunId`, `SnapshotId`,
   `RequestId`, `ArtifactId`, `DecisionId`, `AuthorityVerdictId`,
   `AdapterResultId`, `ReferenceId`.

An evaluator MUST retain the 63 smallest candidate findings under this order
while tracking whether any additional candidate existed. If no additional
candidate existed, it returns all retained findings. If any additional
candidate existed, it returns those 63 findings followed by exactly one stage
255 `finding_limit_exceeded` finding with an empty path and no related identity.
If a complete valid `EvaluationInputIdentity` exists, the `TransitionOutcome`
MUST be `INVALID`; otherwise the result MUST be `InputRejection`. This streaming
selection rule applies even when the validator does not materialize every
candidate finding.

The stable minimum finding codes are:

| Stage key | Codes |
|---:|---|
| 1 | `unsupported_contract_version`, `unknown_field`, `duplicate_field`, `invalid_type`, `invalid_unicode`, `limit_exceeded` |
| 2 | `invalid_identity`, `duplicate_identity`, `missing_reference`, `reference_mismatch` |
| 3 | `run_mismatch`, `snapshot_mismatch` |
| 4 | `terminal_run`, `revision_conflict`, `revision_exhausted`, `request_id_reuse` |
| 5 | `authority_mismatch`, `authority_producer_unaccepted`, `authority_policy_unaccepted`, `authority_denied`, `authority_indeterminate` |
| 6 | `adapter_missing`, `adapter_request_mismatch`, `adapter_run_mismatch`, `adapter_revision_mismatch`, `adapter_snapshot_mismatch`, `adapter_definition_mismatch`, `adapter_operation_mismatch`, `adapter_version_unaccepted`, `adapter_producer_unaccepted` |
| 7 | `adapter_result_invalid` |
| 255 | `finding_limit_exceeded` |

Emission is closed and deterministic:

- `unsupported_contract_version` is emitted once at the contract-version path.
- `unknown_field` or `duplicate_field` is emitted once for each unique offending
  field path; repeated occurrences of the same duplicate path do not add
  findings.
- `invalid_type`, `invalid_unicode`, or `limit_exceeded` is emitted once for
  each unique field path failing that respective rule.
- `invalid_identity` is emitted once for each identity path with invalid shape;
  `duplicate_identity` is emitted once for each repeated typed identity in one
  list, related to that identity.
- `missing_reference` is emitted once for each absent required reference path;
  `reference_mismatch` is emitted once for each wrong-kind or unequal complete
  reference not assigned a more specific code below.
- `run_mismatch` and `snapshot_mismatch` are emitted at stage 3 only when the
  complete request run or expected snapshot differs from the prior run. No
  adapter field is inspected at stage 3.
- `terminal_run`, `revision_conflict`, `revision_exhausted`, and
  `request_id_reuse` are each emitted once when their named stage 4 condition
  holds.
- Each authority code is emitted once for each structurally valid but failing
  binding, producer, accepted-policy membership, or verdict path named by that
  code.
- Adapter fields are inspected only after an exactly bound `AUTHORIZED` verdict.
  Each stage 6 adapter code is emitted once for the exact request, run, revision,
  snapshot, definition, operation, version, or producer binding named by that
  code. `adapter_result_invalid` is emitted at stage 7 only for a bound adapter
  result whose result-kind/successor combination or successor transition is
  inconsistent.
- `finding_limit_exceeded` is emitted only by the overflow rule.

When multiple rules fail at distinct paths, every applicable finding is emitted
subject to the bound. When rules overlap at one path, the most specific named
code above is the only code emitted for that path.

This finding-code set is closed for `0.2.0`. A conforming evaluator MUST NOT
add another code to `TransitionOutcome`, `InputRejection`, or generated audit
events. Additional implementation diagnostics MUST remain outside normative
core records. Adding a normative code requires a new contract version.

### Decisive-stage outcome mapping

The evaluator MUST choose the result kind from the first decisive validation
stage reached:

1. any stage 1 or stage 2 preconstruction failure → `InputRejection`; an
   inconsistent run/definition/snapshot domain input at stage 3 → `INVALID`;
2. terminal run, expected revision mismatch, or maximum active revision →
   `CONFLICT`; changed-content
   reuse of one `IdempotencyKey` is handled by replay validation before normal
   transition evaluation;
3. structurally valid but mismatched or unaccepted authority evidence →
   `INVALID`;
4. valid `DENIED` or `INDETERMINATE` authority verdict → `BLOCKED`;
5. missing, mismatched, unaccepted, or internally invalid adapter result →
   `INVALID`;
6. adapter `NOT_ENABLED` → `NOT_ENABLED`;
7. adapter `BLOCKED` → `BLOCKED`;
8. adapter `INFRASTRUCTURE_FAILURE` → `INFRASTRUCTURE_FAILURE`; and
9. valid adapter `SUCCESSOR` and permitted state transition → `APPLIED`.

Once a decisive stage produces a non-applied outcome, later semantic stages
MUST NOT be consulted. Within the decisive stage, all findings are accumulated
subject to the finding bound.

## Idempotency, replay, and recovery boundary

The complete `IdempotencyKey` is mandatory. A replay validator accepts either
no retained history or one retained tuple containing the complete retained
`EvaluationInputIdentity` and transition outcome for that key.

When retained history is supplied:

- If the candidate `EvaluationInputIdentity` is semantically equal to the
  retained identity, the validator MUST return the retained outcome unchanged.
- If it is semantically different while its `IdempotencyKey` is equal, the
  validator MUST return a `ReplayRejection` containing exactly its deterministic
  `ReplayRejectionId`, both complete evaluation identities, contract version,
  `request_id_reuse`, and no transition outcome or successor.

A `ReplayRejection` is validation evidence and MUST NOT be represented as a
second `TransitionOutcome`, a new run revision, or a mutation of the retained
outcome.

When retained history is absent, the evaluator MUST NOT claim to detect prior
reuse of the key. It performs one pure evaluation. Semantically equal complete
evaluation identities produce the same semantic outcome and structural
outcome/audit identities; any different outcome-determining input produces a
different `OutcomeId`. A runtime MUST retain authoritative idempotency history
before claiming cross-invocation duplicate detection or rejecting key reuse.

Semantic replay compares complete typed records, ordered sequences, and digest
references field by field. Version `0.2.0` does not claim byte-equivalent
serialization. Byte-equivalent replay requires a separately accepted canonical
serializer.

The core performs no persistence and no external effects. A future runtime MUST
atomically retain the idempotency key, complete request, request digest, prior
revision, outcome, and commit status before claiming exactly-once state
application. An external-effect adapter MUST define its own idempotency and
crash-recovery protocol before production use. Passing core replay tests MUST
NOT be represented as evidence that an external effect is exactly once.

## Dependency direction and effect boundary

The core MAY depend only on the Python standard library and separately accepted
Project Koios foundation contracts that are independent of workflow backends,
persistence, UI, adapters, and applications.

Dependencies point inward through typed records or protocols, never through
outward imports from the core:

```text
UI / API / CLI
runtime and persistence
authority-policy boundary
external execution adapters
managed-project adapters
engine adapters
        ↓
workflow core
```

The colored-Petri-net kernel remains a sibling backend and MUST NOT import the
core:

```text
workflow core ← core-to-Petri adapter → colored-Petri backend
```

The core MUST NOT select a Petri transition, invoke a tool or calculator, poll
infrastructure, read or write a database, mutate a run in place, authenticate an
evidence producer, dereference an artifact, decide scientific acceptance, or
publish an artifact. Dependency-direction tests MUST enforce these boundaries
for any implementation claiming conformance.

## Serialization boundary

Internal core records MUST use frozen dataclasses or ordinary immutable domain
classes. This contract does not select a public wire format.

A provisional parser or serializer used only for conformance evidence MUST:

- identify itself and its exact implementation commit;
- reject unknown and duplicate fields;
- enforce all byte and cardinality bounds before domain construction;
- preserve typed nominal identities and ordered-list order;
- declare its digest canonicalization identity and version when producing a
  content digest; and
- make no compatibility or canonical-byte promise outside its documented
  conformance-vector scope.

## Pre-acceptance evidence and lifecycle gates

The contract is technically ready to be considered for acceptance only when:

- every normative record and transition rule above has no unresolved
  `MUST_FIX` finding;
- executable specification examples cover every outcome kind, status
  transition, validation stage, bound, and replay branch;
- conformance vectors demonstrate nominal identity, digest-reference,
  deterministic finding-order, and dependency-direction behavior;
- a separately authorized disposable adapter/consumer spike binds every
  required adapter-result field without importing Petri or application types
  into the core;
- one named prospective consumer owner reviews the spike and records whether
  the proposed vocabulary is sufficient without transferring domain authority;
- the acceptance decision explicitly bounds the still-unimplemented runtime,
  adapter, wire, and consumer compatibility claims;
- the exact specification commit is identified; and
- no unresolved `MUST_FIX` finding remains.

These are specification and feasibility gates. They do not authorize or prove
a production core implementation. After acceptance, implementation requires a
separate owner-task authorization, an implementation commit, full unit, lint,
type, build, isolated-install, dependency-direction, and conformance-vector
validation, and a distinct technical verification outcome.

## Deferred decisions

This contract does not select or authorize:

- a public wire format, canonical public serializer, or compatibility duration;
- a persistence or event-store implementation;
- a scheduler or dispatch model;
- cryptographic authentication or the owning authority policy;
- the colored-Petri adapter;
- a managed-project adapter;
- consumer migration or shadow-replay thresholds;
- release and rollback procedures; or
- deprecation and removal of the source implementation.

Deferring those decisions is valid only while no conformance or acceptance
claim implies that they already exist. If a feasibility spike shows that the
core requires Petri-specific or application-specific semantics, the proposal
MUST be revised or abandoned rather than importing that authority into the
core.
