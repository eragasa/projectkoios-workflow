# Append-only local workflow runtime contract

## Contract metadata

| Field | Value |
|---|---|
| Contract ID | `projectkoios.workflow.runtime` |
| Target version | `0.1.0` |
| Status | Candidate with bounded local Slice A implementation |
| Specification revision | Git commit containing this document |
| Owner | `projectkoios-workflow` |
| Acceptance authority | Project Koios operator after required reviews |
| Architecture record | [`ADR20260920`][workflow-tracks-adr] |
| Task | [`WORKFLOW-RUNTIME-01`][workflow-runtime-task] |
| Predecessor | None registered |
| Supersedes | None while candidate |
| Dependencies | `projectkoios.workflow.core@0.1.0` (Proposed) |
| Consumers | Local private Project Koios control-plane adapters |
| Compatibility | Unknown; no promise while candidate |
| Implementation bindings | `projectkoios.workflow.persistence`; `projectkoios.workflow.runtime`; WF.1 core at [`fd9ca760`][wf1-core-baseline] |
| Effective baseline | None while candidate |

## Status

Candidate for implementation review. The separately authorized Slice A
reference implementation is bounded to local, private, append-only run start,
request preflight/reservation, pure transition processing, identity-chain
replay, and history verification.

This document does not authorize external dispatch, scheduling, claims, leases,
background execution, production use, release, consumer migration, public API
binding, lifecycle action, publication, or CPN promotion. The workflow-core
contract remains Proposed while this first runtime consumer tests its
boundaries.

## Normative scope and conformance

The normative contract begins at **Authority model** and continues through
**Synthetic conformance vectors**, except for text explicitly marked
informative. **Acceptance gates** and **Stop conditions** are also normative.
Purpose, scope summaries, terminology explanations, the consumer-fit assessment,
deferred decisions, and consequences are informative.

The capitalized words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**,
**SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and
**OPTIONAL** have their meanings from the Project Koios contract-governance
policy. Lowercase uses are informative.

Conformance subjects are:

- the runtime orchestrator, for preflight, authority, reservation, ordering,
  final processing, and recovery obligations;
- the authoritative event store, for compare-and-append, predecessor-chain,
  idempotency-retention, and immutable-history obligations;
- adapter planners, for deterministic effect-free planning;
- deployment workers, for attempt-bound execution and evidence reporting;
- reconcilers, for query-only ambiguity resolution;
- projection builders, for disposable and rebuildable read models; and
- replay implementations, for effect-free reconstruction and verification.

A conformance claim identifies this contract ID and target version, the exact
specification and implementation commits, each claimed subject, the applicable
synthetic vectors, and their validation result. Passing conformance evidence
does not accept this contract or grant implementation, deployment, scientific,
lifecycle, release, publication, migration, or CPN authority.

## Purpose

The runtime coordinates durable workflow attempts around the pure,
engine-neutral core. It records immutable evidence before and after external
work, rejects stale or unauthorized requests before dispatch, prevents known
duplicate effects, and reconstructs current state from append-only history.

The runtime does not make application artifacts, external systems, SQLite read
models, clocks, worker processes, or workflow engines authoritative for core
workflow history.

## Scope

Slice A owns:

- append-only per-run event history in one explicit private local store;
- exact expected-head and expected-revision conflict checks;
- run-scoped request-idempotency retention and identical-retry lookup;
- active-occurrence reservation;
- pure core preflight and final transition processing;
- deterministic, effect-free history reconstruction; and
- closed corrupt, incompatible, conflict, error, and indeterminate outcomes.

Later slices may add planning, dispatch authorization, claims, leases,
reconciliation, snapshots, and disposable projections only after their own
acceptance gates. Application or deployment adapters retain application
operations, artifact-store access, domain policy, and all external effects.

## Non-goals

This contract does not:

- add persistence, dispatch, or policy imports to
  `projectkoios.workflow.core`;
- define a public wire format; Slice A serialization is private and versioned;
- select storage for remote, multi-operator, or production deployment;
- define HTTP, browser, or operator-interface contracts;
- define ingestion or scientific artifact formats;
- authorize human, architecture, scientific, lifecycle, publication, release,
  deployment, or migration decisions;
- require the colored-Petri-net backend; or
- accept the separate workflow-kernel ownership transfer; or
- make GitHub, browser projections, organizer proposals, or API state
  authoritative.

## Terminology

### Runtime event

An immutable, bounded record of one accepted observation or runtime decision.
Events form the authoritative per-run history for this runtime contract.

### Occurrence

One durable attempt to carry one exact transition request from retained input
through planning, possible execution, reconciliation, and final core outcome.
An occurrence is not an external effect and does not grant authority.

### Plan

A deterministic, effect-free proposal produced from exact supplied inputs. A
plan identifies operations, adapter configuration, expected evidence, effect
intents, bounds, and idempotency tokens. Planning performs no external I/O.

### Effect intent

A bounded reference describing work that an authorized deployment worker may
perform. It contains opaque identities and digests, never protected payloads,
credentials, source excerpts, or machine paths.

### Execution evidence

Immutable evidence returned by a worker after an effect attempt. It states a
known outcome or an explicit ambiguity and binds the exact occurrence, attempt,
plan, effect intent, dispatch authorization, adapter, configuration, and
idempotency token.

### Reconciliation

A query-only or evidence-inspection operation that resolves whether an
ambiguous effect occurred. Reconciliation must not repeat the effect.

### Projection

A disposable query representation derived from authoritative events. A
projection may be rebuilt and may never repair or replace event history.

## Authority model

Authority MUST be layered and fail-closed:

1. The core preflight action MUST check deterministic structural binding.
2. The runtime or owning application policy MUST resolve the referenced
   authority evidence and verify authenticity, applicability, expiry, and
   revocation.
3. A separately scoped dispatch authorization MUST bind one exact plan and
   effect intent before a worker MAY act.
4. The worker MUST report evidence and MUST NOT grant acceptance or lifecycle
   authority.
5. Final core processing MUST check supplied adapter or infrastructure
   evidence.

Slice A performs only structural preflight. It retains the supplied immutable
authority-reference identity but does not claim to verify authenticity, expiry,
revocation, or policy applicability. Because Slice A cannot dispatch an effect,
advance publication state, or grant a lifecycle decision, this deferred policy
verification does not create execution authority.

A successful preflight, enabled plan, worker success, replay match, or technical
validation MUST NOT establish any protected human or domain decision.

Authority evidence MUST be referenced by immutable identity and version. It
MUST NOT be copied into workflow state. A changed subject, operation, plan,
adapter, configuration, authority version, or effect intent MUST require new
applicable authority.

## Two-stage adapter protocol

### Stage A: preflight and deterministic planning

Before planning, the runtime MUST:

1. loads the exact definition, run, prior snapshot, and transition request;
2. calls `WorkflowTransitionValidator`;
3. rejects all structural findings without calling a planner or worker;
4. verifies externally owned authority evidence under the owning policy;
5. resolves the exact adapter and configuration identities; and
6. atomically retains the request and reserves its run revision.

`REQUEST_RETAINED` is also the active-occurrence reservation for the tuple of
run identity and expected revision. Exactly one distinct request MAY own that
reservation. An identical idempotent retry MUST return the retained
occurrence. A different request for the reserved revision MUST record
`REQUEST_CONFLICT_RECORDED`, remain ineligible for planning or execution, and
return a revision-reserved conflict.

The planner MUST consume only immutable supplied records and return exactly one
bounded result:

- `PLANNED`, with an immutable plan and zero or more effect intents;
- `DISABLED`, with bounded reasons and no effect intents; or
- `PLAN_REJECTED`, with bounded findings and no effect intents.

`PLAN_REJECTED` is a terminal pre-dispatch occurrence state. It MUST record the
rejection, release the reservation because no effect began, and produce no core
transition. An identical retry MUST return the retained rejection. Changed
inputs or configuration MUST require a new request identity and reservation.
`DISABLED` instead MUST produce bounded disabled adapter evidence for final
core processing.

A plan identity MUST derive from at least:

- workflow definition identity;
- run and prior-state identities;
- transition-request identity;
- expected revision;
- adapter and adapter-configuration identities;
- ordered input-reference identities;
- ordered effect-intent identities;
- request bounds; and
- runtime-contract version.

The planner MUST NOT read a clock, filesystem, database, network service,
random source, environment secret, mutable GitHub state, or artifact payload.
Facts needed for planning MUST arrive as versioned input references.

### Stage B: authorized effect execution

Planning MUST NOT authorize execution. Immediately before every effect attempt,
the runtime MUST revalidate authenticity, applicability, expiry, and revocation
under the owning policy. It then records a fresh immutable
dispatch-authorization reference that binds:

- one occurrence and attempt identity;
- one plan identity;
- one effect-intent identity;
- one worker or worker-class identity;
- one external idempotency token;
- one authority-evidence identity and version;
- one authority-verification decision and observation identity;
- a bounded validity condition or expiry observation;
- exact scope and limits; and
- an owning-policy decision identity.

The dispatch authorization applies to exactly one attempt and MUST be current
at worker handoff. It MUST NOT be reused by another attempt or after expiry,
revocation, policy-version change, or other loss of applicability. Failed
revalidation MUST record `AUTHORITY_REJECTED` or new reauthorization evidence
and prevent worker execution.

The worker receives a deployment-owned request resolved outside workflow state.
The runtime MUST supply only compact references and authorization evidence. The
worker MUST return one of:

- `SUCCEEDED`, with bounded produced-evidence references;
- `KNOWN_NOT_APPLIED`, with bounded failure evidence and retry classification;
- `KNOWN_APPLIED_WITH_FAILURE`, with evidence requiring application policy;
- `AMBIGUOUS`, requiring reconciliation before any retry; or
- `REJECTED_BEFORE_EFFECT`, proving no external effect began.

An exception, timeout, lost connection, expired lease, or worker disappearance
is not proof that no effect occurred. Such an occurrence MUST enter
reconciliation unless retained evidence proves `KNOWN_NOT_APPLIED` or
`REJECTED_BEFORE_EFFECT`.

### Final core processing

After all required effect intents have non-ambiguous evidence, the adapter
MUST construct bounded `WorkflowAdapterEvidence` or
`WorkflowInfrastructureFailureEvidence`. The runtime MUST then call
`WorkflowTransitionProcessor` with the exact preflight records and supplied
evidence.

The runtime MUST append the resulting immutable core outcome and audit
reference before advancing its current pointer. Invalid final evidence MUST NOT
be repaired by mutating the plan, worker report, prior event, or core outcome.

## Conceptual records

Slice A binds its exact private representation in
`projectkoios.workflow.runtime` and its opaque persistence contract in
`projectkoios.workflow.persistence`. Later slices MUST preserve nominal
identity domains for at least:

- runtime event;
- occurrence;
- attempt;
- adapter configuration;
- plan;
- effect intent;
- dispatch authorization;
- worker claim;
- lease;
- execution evidence;
- reconciliation request and result;
- event-log head; and
- projection generation.

Every immutable runtime record MUST include a contract version, exact upstream
identities, and bounded references. The opaque persistence envelope separately
binds stream, revision, predecessor, schema, content, payload, and idempotency
identities. Content-derived identities establish integrity, not truth, actor
authenticity, authority, or domain acceptance.

Identity construction MUST remain acyclic:

- an occurrence identity derives from the run, prior state, expected revision,
  request, request idempotency identity, and runtime-contract version;
- an effect-intent identity derives from the occurrence, adapter configuration,
  intent ordinal, operation kind, bounded input references, and expected output
  contract;
- a plan identity derives from the occurrence, adapter configuration, ordered
  effect-intent identities, bounds, and runtime-contract version;
- an attempt identity derives from the occurrence and attempt ordinal; and
- execution and reconciliation identities derive from the exact plan, intent,
  attempt, and supplied evidence.

An identity MUST NOT directly or indirectly include itself. Stable logical
identities MUST remain distinct from immutable evidence identities.

## Append-only history

### Event envelope

A runtime event MUST record at least:

- event identity and event kind;
- run identity;
- per-run event ordinal;
- predecessor-event identity, except for genesis;
- occurrence and request identities when applicable;
- observed core revision and state identity;
- bounded evidence references;
- producer implementation and contract versions; and
- integrity identity over all semantic fields.

Wall-clock values MAY be retained as observations for operations, but they
MUST NOT determine event identity, replay order, or transition precedence.

### Event kinds

Slice A has the following closed event vocabulary:

- `run_started`;
- `request_retained`;
- `request_conflict_recorded`;
- `preflight_rejected`;
- `transition_recorded`.

The private type also reserves `plan_recorded`, `plan_disabled`,
`plan_rejected`, and `terminal_failure_recorded`, but Slice A does not produce
them. A later slice MUST add its event semantics and conformance vectors before
use. An implementation MAY use more specific internal records, but it MUST map
them to accepted semantics without deleting or rewriting prior evidence.

### Atomic append

Appending events for one run MUST use compare-and-append against the exact
retained head identity and expected event ordinal. A mismatch MUST fail with a
conflict and append nothing. Store commits distinguish `committed`, exact
`idempotent` replay, `conflict`, `indeterminate`, and `error`; an indeterminate
result MUST be resolved by readback before any changed append.

Request retention and its first event MUST commit before planning or dispatch.
A plan MUST commit before dispatch authorization. Attempt-bound dispatch
authorization MUST commit before the worker call. Execution or ambiguity
evidence MUST commit before final core processing. The final core outcome MUST
commit before a mutable current pointer or read projection advances.

The runtime MUST NOT assume that an external effect and the event store share a
transaction. Recovery therefore relies on external idempotency and
reconciliation rather than pretending that a database transaction covers both.

### Active occurrence reservation

For each tuple of run identity and core revision, at most one occurrence MAY be
active and effect-eligible. The compare-and-append that records
`REQUEST_RETAINED` MUST atomically acquire this reservation.

An identical idempotent retry MUST resolve to the reservation owner. A distinct
same-revision request MUST record `REQUEST_CONFLICT_RECORDED`, MUST NOT plan,
claim, authorize, or dispatch, and MUST return a revision-reserved conflict.

The reservation MAY release only after:

- a terminal pre-dispatch rejection of the reservation owner proves no effect
  began;
- final core processing and `TRANSITION_RECORDED` complete; or
- reconciliation and owning policy establish a terminal resolution.

Ambiguity, lease expiry, worker disappearance, partial application, and known
application with failure MUST retain the reservation. They MUST NOT make a
second occurrence effect-eligible.

## Deterministic ordering

Per-run event ordinal and predecessor identity MUST define authoritative event
order. No total order is asserted across independent runs.

Occurrence precedence MUST be determined by:

1. expected core revision;
2. the successful `REQUEST_RETAINED` event ordinal;
3. transition-request identity;
4. occurrence identity; and
5. attempt ordinal within that occurrence.

The compare-and-append winner records precedence for concurrent arrivals. The
runtime does not claim deterministic selection across requests that were never
retained; it deterministically replays the recorded winner. A losing append
MUST reload authoritative history. An identical request resolves to the winner;
a distinct same-revision request receives a revision-reserved conflict and
remains ineligible for effects.

A lease, queue order, process identifier, or wall clock MAY affect which worker
observes work first, but MUST NOT change retained occurrence precedence or
replay semantics.

## Idempotency

Slice A defines request-idempotency scope as one workflow-run identity. The
runtime retains the first exact transition-request identity for each core
`WorkflowIdempotencyIdentity` in that run's event chain. The request identity is
the semantic digest because the core derives it from every request semantic
field, including run, prior state, revision, operation, ordered references,
actor, authority, bounds, and idempotency identity. Comparisons MUST NOT cross
run streams.

The lower opaque revision store uses a store-global idempotency identity that
binds one exact candidate envelope. The runtime repository derives distinct
purpose-prefixed store keys from content-identified events; these keys are not
core request-idempotency identities.

- Identical reuse MUST return the retained occurrence or terminal evidence.
- Changed reuse MUST fail closed and MUST NOT plan or dispatch.
- An identical retry after a terminal core outcome MUST return that outcome.
- An identical retry during active execution MUST return current occurrence
  state.
- An identical retry during ambiguity MUST return reconciliation-required
  state.

Each effect intent MUST have an external idempotency token derived from
immutable occurrence and intent identities. A deployment adapter MUST declare
whether the external system supports token lookup, idempotent execution, both,
or neither.
An effect with neither capability MUST NOT be automatically retried after an
ambiguous boundary.

## Claims and leases

A claim grants temporary permission to work on one retained occurrence. It does
not grant operation authority or ownership of the run. Only the active
reservation owner MAY receive a claim.

A lease MUST bind a claim, worker identity, occurrence, attempt ordinal,
lease-policy version, and observed expiry evidence. Lease duration and clock
source MUST be runtime policy inputs and MUST NOT define identity or replay
order.

Expiry permits another worker to reconcile the occurrence. It does not prove
that the prior worker performed no effect and MUST NOT by itself permit repeated
execution. Every later effect attempt MUST use a new claim and fresh
attempt-bound dispatch authorization.

At most one active claim MAY be recorded for an occurrence under one retained
head. Conflicting claims MUST fail through compare-and-append.

## Failure and retry model

Failures MUST be classified by evidence, not exception type alone:

| Class | Effect status | Automatic retry |
|---|---|---|
| Structural rejection | Not dispatched | No; submit a corrected request |
| Authority rejection | Not dispatched | No; obtain new policy evidence |
| Planning rejection | Not dispatched | After changed inputs or configuration |
| Rejected before effect | Proven not applied | Allowed by bounded policy |
| Known not applied | Proven not applied | Allowed by bounded policy |
| Known applied failure | Applied or partial | Policy or compensation only |
| Ambiguous | Unknown | Never before reconciliation |
| Reconciliation unresolved | Unknown | Manual or policy-owned resolution |
| Terminal runtime failure | Any retained status | No automatic retry |

Retry policy MUST be versioned and bounded by maximum attempts. Exhaustion MUST
record a terminal failure without deleting earlier attempts. Compensation, when
a domain supports it, is a new authorized operation rather than history
reversal.

## Reconciliation

Reconciliation MUST accept the exact occurrence, plan, intent, external
idempotency token, and all retained worker/infrastructure evidence. It MAY query
an external idempotency or receipt interface, but it MUST NOT invoke the original
effect.

A reconciliation result MUST be one of:

- `CONFIRMED_APPLIED`;
- `CONFIRMED_NOT_APPLIED`;
- `CONFIRMED_PARTIAL`;
- `STILL_AMBIGUOUS`; or
- `EVIDENCE_INVALID`.

`CONFIRMED_NOT_APPLIED` MAY permit a new bounded attempt after fresh authority
verification. `CONFIRMED_APPLIED` continues with retained result evidence.
Partial or unresolved outcomes MUST require application policy or explicit
human action.

## Recovery matrix

| Retained boundary at interruption | Recovery action | Effect rule |
|---|---|---|
| Before request retention | Resubmit exact request | No retained effect |
| Retained request, no plan | Re-run planning | No worker call yet |
| Plan, no dispatch authority | Revalidate authority | No worker call yet |
| Authorized, no conclusive report | Reconcile first | Never assume no effect |
| Report, no core outcome | Re-run pure processing | Never repeat effect |
| Core outcome, stale pointer | Rebuild pointer | Never repeat effect |
| Current pointer, stale projection | Rebuild projection | Never repeat effect |
| Expired lease while uncertain | Reconcile | Never infer non-execution |

Recovery MUST read authoritative events, verify their identities and
predecessor chain, reconstruct occurrence state, and resume only at an allowed
boundary. A corrupt or missing event chain MUST fail closed; a projection MUST
NOT fill the gap.

## Snapshots and projections

Immutable runtime snapshots MAY accelerate recovery but MUST derive from an
exact event-log head. A snapshot MUST record its source head, source ordinal,
core run and state identities, active occurrences, and contract version.

A mutable current pointer MAY identify the latest verified snapshot. Losing or
corrupting the pointer MUST NOT destroy history; it is rebuilt from events.

For private single-operator Slice A, the hardened
`SQLiteAtomicRevisionStore` MAY be the authoritative local event history. It
MUST use one explicit absolute path, reject symlink/non-regular database paths,
require an operator-owned private parent, use `0600` database and `0700` parent
permissions, enable foreign keys and full synchronization, use non-WAL
journaling, verify an exact format/schema, and verify every retained envelope.

This exception does not approve SQLite as remote, shared, multi-operator, or
production authority. API responses, browser state, organizer databases,
GitHub state, and materialized views remain disposable projections and MUST NOT
repair or replace the private event chain. Backup, archival, and restore policy
remain outside Slice A.

## Artifact-reference verification

The runtime MAY ask an owning artifact store to verify identity, digest,
availability, and declared media or schema metadata. Verification MUST return a
bounded evidence reference. The runtime MUST NOT store source bytes, transcript
text, full chapter maps, credentials, private paths, or protected excerpts.

Artifact existence MUST NOT establish extraction quality, review acceptance,
scientific validity, rights clearance, lifecycle activation, or publication
authority.

## Initial course-review consumer

Slice A's first consumer is the metadata-only local course-review workflow. Its
closed stages are:

1. `proposal_observed`;
2. `course_identity_candidate`;
3. `sanitization_evidence_required`;
4. `manual_review_required`; and
5. either `reviewed_retained` or `reviewed_excluded`.

`published` is deliberately not a stage or operation. Publication remains a
separately authorized catalog mutation outside this workflow.

An `OrganizerTeachingProposalReference` is a typed input containing only
bounded proposal, proposal-set, model, catalog-revision, course, source-metadata
digest, and fixed `life_domain=teaching` identities. It MUST NOT contain a
source path, payload, student information, authority grant, or approval. The
organizer adapter MAY construct deterministic candidate-transition evidence,
but the transition request MUST carry a separately supplied core authority
reference. The adapter performs no payload read, move, rename, deletion,
upload, approval, publication, or external dispatch.

The candidate definition admits only the
`proposal_observed` to `course_identity_candidate` operation. It does not merely
omit adapters for later transitions: those operation identities are absent and
therefore fail core preflight. Later sanitization and manual-review transitions
require a new reviewed definition version, evidence contracts, and adapters. A
review-retained outcome MUST NOT imply public-material clearance or publication
approval.

## Baseline deterministic adapter

WF.2 MUST retain an engine-neutral baseline planner and adapter path. It MUST
consume only supplied references, produce bounded plans and core adapter
evidence, and require no CPN types or kernel.

The baseline path is the authoritative comparison path during future CPN shadow
replay. CPN enablement, equality, or promotion MUST NOT weaken baseline checks
or remove baseline rollback.

## Dry run

A dry run MUST execute structural preflight, owning-policy authority inspection
in non-granting mode, and deterministic planning. It MUST NOT perform any claim,
dispatch, external effect, final transition, current-pointer update, or
lifecycle action.

Dry-run output is a bounded proposal bound to exact inputs and configuration. It
is not execution evidence and MUST NOT be supplied as a successful worker
result.

## Privacy and logging

Events, logs, exceptions, projections, and public task records MUST contain
compact typed references only. They MUST exclude:

- artifact payloads and source excerpts;
- PDF or transcript content;
- full chapter maps;
- credentials and authorization secrets;
- private or machine-specific paths;
- private workflow payload bodies; and
- mutable GitHub state copied as runtime authority.

Operational diagnostics MUST use bounded reason codes and sanitized messages.
Exact protected evidence MUST remain in its owning store.

## Replay

Slice A identity-chain replay verifies:

- every persistence-envelope digest;
- canonical event bytes and content identity;
- one acyclic, contiguous predecessor/ordinal chain;
- one run identity across the chain;
- retained request-idempotency and reservation decisions; and
- observed core revision and state identities.

Slice A does not serialize complete `WorkflowRun`, `WorkflowStateSnapshot`,
transition input, or transition outcome records. A later action must resupply
those immutable core records, and the runtime checks their content-derived
identities against the retained head before processing. Slice A therefore MUST
NOT claim full core semantic recomputation from the event store alone. Such a
claim requires a later accepted canonical core-record retention contract and
replay vectors.

Replay MUST NOT call workers, external systems, clocks, random sources,
artifact payload readers, or CPN execution. External results MUST be supplied as
retained evidence. Slice A runtime events use canonical UTF-8 JSON under
private schema identity `projectkoios.workflow.runtime-event:1`; decoding MUST
reject duplicate keys, unknown or missing fields, noncanonical bytes,
unsupported versions, and content-identity mismatch. This is not a public wire
compatibility promise.

## Synthetic conformance vectors

Slice A fixtures MUST define expected retained events and prohibited calls for
vectors 2--5, 9--13, 22, 25, 27, and 28 below, plus exact start/reopen,
canonical serialization, payload-bound, store-format, file-safety, and
envelope-integrity cases. Vectors involving plans, workers, attempts, leases,
external effects, reconciliation, pointers, or projections are mandatory gates
for the later slice that introduces those capabilities.

The complete runtime vector inventory is:

1. valid preflight and deterministic plan;
2. stale revision rejected before planning;
3. unknown operation rejected before planning;
4. terminal run rejected before planning;
5. structurally mismatched authority rejected before planning;
6. externally invalid, expired, or revoked authority rejected before dispatch;
7. planning rejection recording `PLAN_REJECTED` and no core transition;
8. disabled planning producing distinct adapter evidence;
9. two distinct same-revision requests permitting only the reservation winner
   to plan, claim, authorize, or dispatch;
10. identical request retry returning retained state;
11. changed idempotency reuse failing closed within one declared scope;
12. identical and changed idempotency reuse across distinct scopes;
13. conflicting concurrent append;
14. duplicate worker claim;
15. lease expiry followed by reconciliation, not execution;
16. a retry receiving a new attempt-bound authorization after revalidation;
17. expired or revoked authority blocking a later attempt;
18. crash at each recovery-matrix boundary;
19. known-not-applied bounded retry;
20. ambiguous timeout blocking retry;
21. reconciliation confirming applied and confirming not applied;
22. final evidence mismatch rejected by the core;
23. retained outcome with stale pointer;
24. full projection rebuild;
25. corrupt event-chain detection;
26. aggregate core bounds exceeded;
27. privacy-safe diagnostic output; and
28. baseline operation with no CPN package involvement.

Fixtures MUST use synthetic identities and payload-free references. Private
documents MAY supplement later operational validation but MUST NOT enter Git or
public logs.

## Workflow-core consumer-fit assessment

The merged WF.1 implementation supplies the required pure boundaries:

- `WorkflowTransitionPreflightInput` and `WorkflowTransitionValidator` support
  pre-dispatch structural rejection without adapter evidence;
- `WorkflowTransitionProcessor` reuses the same structural rules for final
  processing;
- authority references support deterministic subject and operation binding
  while leaving authenticity and policy evaluation external;
- adapter and infrastructure evidence bind exact requests and prior states;
- immutable outcomes and audit events support retained replay; and
- core modules do not import runtime, persistence, UI, ingestion, or CPN code.

This design does not currently require a WF.1 code change. Runtime occurrence,
plan, claim, lease, dispatch, reconciliation, and persistence identities belong
outside the core. Run-start persistence and audit evidence are also WF.2
responsibilities.

The core contract should remain Proposed until review confirms that this runtime
contract and at least one deployment-adapter design can consume it without
moving runtime or application concerns into the core.

## Deferred decisions

The following decisions remain outside Slice A and must be accepted before the
slice that needs them:

- schema migration beyond fail-closed version incompatibility;
- configured application data-root resolution;
- clocks, leases, claims, scheduling, and background execution;
- planning and deployment-adapter code ownership;
- effect idempotency, dispatch, reconciliation, and retry policy;
- snapshot and projection storage;
- retention, archival, backup, and restore policy;
- public wire compatibility;
- API and browser contracts; and
- release and consumer-migration policy.

## Acceptance gates

Slice A implementation review requires:

- workflow-core consumer fit with no unresolved blocking finding;
- exact runtime identities, collection bounds, and canonical private bytes;
- run-scoped request-idempotency and store-global envelope-idempotency tests;
- compare-and-append, reopen, corruption, format, and file-safety tests;
- privacy review confirming metadata-only, payload-free runtime events;
- effect-free dependency review; and
- separate operator acceptance before merge or consumer integration.

Planning or external-effect implementation remains blocked until:

- its contract extension and synthetic vectors are reviewed and accepted;
- the first deployment adapter declares idempotency and reconciliation
  capability;
- authenticity, applicability, expiry, and revocation checks are designed;
- attempt, claim, lease, dispatch, ambiguity, and recovery semantics are
  accepted; and
- implementation is separately authorized.

## Stop conditions

Stop before implementation if:

- authority verification cannot complete before dispatch;
- an ambiguous effect could be retried without reconciliation;
- an external effect lacks a safe idempotency, lookup, compensation, or manual
  resolution boundary;
- workflow-core changes would introduce persistence, runtime, application, or
  CPN dependencies;
- event history could be overwritten or repaired from a projection;
- protected payloads or private paths would enter runtime state; or
- external-effect implementation, merge, release, migration, deployment, or
  CPN promotion would begin without separate authorization.

## Consequences

- Slice A can be reviewed against an isolated reference implementation.
- External effects remain outside pure core processing and deterministic
  planning.
- Ambiguous failures become explicit reconciliation states rather than retries.
- Append-only history remains recoverable independently of disposable views.
- The runtime carries additional records for plans, occurrences, claims,
  execution, and reconciliation.
- Slice A makes a private canonical-JSON and hardened-SQLite choice without
  making a public or production compatibility promise.

[workflow-tracks-adr]:
  https://github.com/eragasa/projectkoios/blob/main/docs/adr.20260920.workflow-and-cpn-development-tracks.md
[wf1-core-baseline]:
  https://github.com/eragasa/projectkoios-workflow/commit/fd9ca760c7ed8467062a17411c1df33981d2836e
[workflow-runtime-task]:
  https://github.com/eragasa/projectkoios-workflow/issues/3
