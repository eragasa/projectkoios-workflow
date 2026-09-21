# Append-only local workflow runtime contract

## Contract metadata

| Field | Value |
|---|---|
| Contract ID | `projectkoios.workflow.runtime` |
| Target version | `0.1.0` |
| Status | Proposed |
| Specification revision | Git commit containing this document |
| Owner | `projectkoios-workflow` |
| Acceptance authority | Project Koios operator after required reviews |
| Architecture record | [`ADR20260920`][workflow-tracks-adr] |
| Task | [`WORKFLOW-RUNTIME-01`][workflow-runtime-task] |
| Dependency | Proposed core; merged WF.1 implementation |
| Implementation binding | None while proposed |
| Effective baseline | None while proposed |

## Status

Proposed for design and consumer-fit review only.

This document does not authorize a runtime implementation, persistence
technology, external dispatch, production use, release, consumer migration, or
CPN promotion. The workflow-core contract remains Proposed while this first
runtime consumer tests its boundaries.

## Purpose

The runtime coordinates durable workflow attempts around the pure,
engine-neutral core. It records immutable evidence before and after external
work, rejects stale or unauthorized requests before dispatch, prevents known
duplicate effects, and reconstructs current state from append-only history.

The runtime does not make application artifacts, external systems, SQLite read
models, clocks, worker processes, or workflow engines authoritative for core
workflow history.

## Scope

The proposed runtime owns:

- append-only run-event history;
- immutable runtime snapshots and mutable current pointers;
- expected-head and expected-revision conflict checks;
- idempotency retention and identical-retry lookup;
- deterministic adapter planning;
- externally verified dispatch authority;
- bounded claims and leases;
- execution-result and infrastructure-failure evidence;
- reconciliation of ambiguous external outcomes;
- final core transition processing;
- recovery and semantic replay; and
- disposable read projections.

The runtime coordinates protocols. Application or deployment adapters still own
application operations, artifact-store access, domain policy, and external
effects.

## Non-goals

This contract does not:

- add persistence, dispatch, or policy imports to
  `projectkoios.workflow.core`;
- choose a public wire format or canonical serializer;
- choose SQLite or another database as historical authority;
- define HTTP, browser, or operator-interface contracts;
- define ingestion or scientific artifact formats;
- authorize human, architecture, scientific, lifecycle, publication, release,
  deployment, or migration decisions;
- require the colored-Petri-net backend; or
- accept the separate workflow-kernel ownership transfer.

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
known outcome or an explicit ambiguity and binds the exact occurrence, plan,
effect intent, adapter, configuration, and idempotency token.

### Reconciliation

A query-only or evidence-inspection operation that resolves whether an
ambiguous effect occurred. Reconciliation must not repeat the effect.

### Projection

A disposable query representation derived from authoritative events. A
projection may be rebuilt and may never repair or replace event history.

## Authority model

Authority is layered and fail-closed:

1. The core preflight action checks deterministic structural binding.
2. The runtime or owning application policy resolves the referenced authority
   evidence and verifies authenticity, applicability, expiry, and revocation.
3. A separately scoped dispatch authorization binds one exact plan and effect
   intent before a worker may act.
4. The worker reports evidence; it does not grant acceptance or lifecycle
   authority.
5. Final core processing checks supplied adapter or infrastructure evidence.

A successful preflight, enabled plan, worker success, replay match, or technical
validation does not establish any protected human or domain decision.

Authority evidence is referenced by immutable identity and version. It is not
copied into workflow state. A changed subject, operation, plan, adapter,
configuration, authority version, or effect intent requires new applicable
authority.

## Two-stage adapter protocol

### Stage A: preflight and deterministic planning

Before planning, the runtime:

1. loads the exact definition, run, prior snapshot, and transition request;
2. calls `WorkflowTransitionValidator`;
3. rejects all structural findings without calling a planner or worker;
4. verifies externally owned authority evidence under the owning policy;
5. resolves the exact adapter and configuration identities; and
6. retains the request under its idempotency identity.

The planner consumes only immutable supplied records and returns exactly one
bounded result:

- `PLANNED`, with an immutable plan and zero or more effect intents;
- `DISABLED`, with bounded reasons and no effect intents; or
- `PLAN_REJECTED`, with bounded findings and no effect intents.

A plan identity must derive from at least:

- workflow definition identity;
- run and prior-state identities;
- transition-request identity;
- expected revision;
- adapter and adapter-configuration identities;
- ordered input-reference identities;
- ordered effect-intent identities;
- request bounds; and
- runtime-contract version.

The planner must not read a clock, filesystem, database, network service, random
source, environment secret, mutable GitHub state, or artifact payload. Facts
needed for planning arrive as versioned input references.

### Stage B: authorized effect execution

Planning never authorizes execution. Before dispatch, the runtime records an
immutable dispatch-authorization reference that binds:

- one occurrence identity;
- one plan identity;
- one effect-intent identity;
- one worker or worker-class identity;
- one external idempotency token;
- one authority-evidence identity and version;
- exact scope and limits; and
- an owning-policy decision identity.

The worker receives a deployment-owned request resolved outside workflow state.
The runtime supplies only compact references and authorization evidence. The
worker returns one of:

- `SUCCEEDED`, with bounded produced-evidence references;
- `KNOWN_NOT_APPLIED`, with bounded failure evidence and retry classification;
- `KNOWN_APPLIED_WITH_FAILURE`, with evidence requiring application policy;
- `AMBIGUOUS`, requiring reconciliation before any retry; or
- `REJECTED_BEFORE_EFFECT`, proving no external effect began.

An exception, timeout, lost connection, expired lease, or worker disappearance
is not proof that no effect occurred. Such an occurrence enters reconciliation
unless retained evidence proves `KNOWN_NOT_APPLIED` or
`REJECTED_BEFORE_EFFECT`.

### Final core processing

After all required effect intents have non-ambiguous evidence, the adapter
constructs bounded `WorkflowAdapterEvidence` or
`WorkflowInfrastructureFailureEvidence`. The runtime then calls
`WorkflowTransitionProcessor` with the exact preflight records and supplied
evidence.

The runtime appends the resulting immutable core outcome and audit reference
before advancing its current pointer. Invalid final evidence cannot be repaired
by mutating the plan, worker report, prior event, or core outcome.

## Conceptual records

The exact Python and serialized representations are deferred. Any implementation
must preserve nominal identity domains for at least:

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

Every immutable record includes a contract version, exact upstream identities,
and bounded references. Content-derived identities establish integrity, not
truth, actor authenticity, authority, or domain acceptance.

Identity construction must remain acyclic:

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

No identity may directly or indirectly include itself. Stable logical
identities remain distinct from immutable evidence identities.

## Append-only history

### Event envelope

A runtime event records at least:

- event identity and event kind;
- run identity;
- per-run event ordinal;
- predecessor-event identity, except for genesis;
- occurrence and request identities when applicable;
- observed core revision and state identity;
- bounded evidence references;
- producer implementation and contract versions; and
- integrity identity over all semantic fields.

Wall-clock values may be retained as observations for operations, but they do
not determine event identity, replay order, or transition precedence.

### Event kinds

The initial semantic event set is:

- `RUN_START_RECORDED`;
- `REQUEST_RETAINED`;
- `PREFLIGHT_REJECTED`;
- `AUTHORITY_REJECTED`;
- `PLAN_RECORDED`;
- `PLAN_DISABLED`;
- `DISPATCH_AUTHORIZED`;
- `CLAIM_RECORDED`;
- `EXECUTION_REPORTED`;
- `RECONCILIATION_REQUIRED`;
- `RECONCILIATION_RECORDED`;
- `TRANSITION_RECORDED`;
- `RETRY_ALLOWED`;
- `TERMINAL_FAILURE_RECORDED`; and
- `PROJECTION_CHECKPOINT_RECORDED`.

An implementation may use more specific internal records, but it must map them
to these semantics without deleting or rewriting prior evidence.

### Atomic append

Appending events for one run uses compare-and-append against the exact retained
head identity and expected event ordinal. A mismatch fails with a conflict and
appends nothing.

Request retention and its first event commit before planning or dispatch. A
plan commits before dispatch authorization. Dispatch authorization commits
before the worker call. Execution or ambiguity evidence commits before final
core processing. The final core outcome commits before a mutable current pointer
or read projection advances.

An external effect and the event store cannot share an assumed transaction.
Recovery therefore relies on external idempotency and reconciliation rather
than pretending that a database transaction covers both.

## Deterministic ordering

Per-run event ordinal and predecessor identity define authoritative event order.
No total order is asserted across independent runs.

Occurrence precedence is determined by:

1. expected core revision;
2. the successful `REQUEST_RETAINED` event ordinal;
3. transition-request identity;
4. occurrence identity; and
5. attempt ordinal within that occurrence.

The compare-and-append winner records precedence for concurrent arrivals. The
runtime does not claim deterministic selection across requests that were never
retained; it deterministically replays the recorded winner. A losing append
reloads authoritative history and normally encounters a revision conflict.

A lease, queue order, process identifier, or wall clock may affect which worker
observes work first, but cannot change retained occurrence precedence or replay
semantics.

## Idempotency

The runtime retains the first exact request identity and semantic digest for
each idempotency identity within its declared scope.

- Identical reuse returns the retained occurrence or terminal evidence.
- Changed reuse fails closed and never plans or dispatches.
- An identical retry after a terminal core outcome returns that outcome.
- An identical retry during active execution returns current occurrence state.
- An identical retry during ambiguity returns reconciliation-required state.

Each effect intent also has an external idempotency token derived from immutable
occurrence and intent identities. A deployment adapter must declare whether the
external system supports token lookup, idempotent execution, both, or neither.
An effect with neither capability cannot be automatically retried after an
ambiguous boundary.

## Claims and leases

A claim grants temporary permission to work on one retained occurrence. It does
not grant operation authority or ownership of the run.

A lease binds a claim, worker identity, occurrence, attempt ordinal,
lease-policy version, and observed expiry evidence. Lease duration and clock
source are runtime policy inputs and are not identity or replay order.

Expiry permits another worker to reconcile the occurrence. It does not prove
that the prior worker performed no effect and does not by itself permit repeated
execution.

At most one active claim may be recorded for an occurrence under one retained
head. Conflicting claims fail through compare-and-append.

## Failure and retry model

Failures are classified by evidence, not exception type alone:

| Class | Effect status | Automatic retry |
|---|---|---|
| Structural rejection | Not dispatched | No; submit a corrected request |
| Authority rejection | Not dispatched | No; obtain new policy evidence |
| Planning rejection | Not dispatched | Only after inputs or configuration change |
| Rejected before effect | Proven not applied | Allowed by bounded policy |
| Known not applied | Proven not applied | Allowed by bounded policy |
| Known applied failure | Applied or partial | Policy or compensation only |
| Ambiguous | Unknown | Never before reconciliation |
| Reconciliation unresolved | Unknown | Manual or policy-owned resolution |
| Terminal runtime failure | Any retained status | No automatic retry |

Retry policy is versioned and bounded by maximum attempts. Exhaustion records a
terminal failure without deleting earlier attempts. Compensation, when a domain
supports it, is a new authorized operation rather than history reversal.

## Reconciliation

Reconciliation accepts the exact occurrence, plan, intent, external idempotency
token, and all retained worker/infrastructure evidence. It may query an external
idempotency or receipt interface, but it must not invoke the original effect.

A reconciliation result is one of:

- `CONFIRMED_APPLIED`;
- `CONFIRMED_NOT_APPLIED`;
- `CONFIRMED_PARTIAL`;
- `STILL_AMBIGUOUS`; or
- `EVIDENCE_INVALID`.

`CONFIRMED_NOT_APPLIED` may permit a new bounded attempt. `CONFIRMED_APPLIED`
continues with retained result evidence. Partial or unresolved outcomes require
application policy or explicit human action.

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

Recovery reads authoritative events, verifies their identities and predecessor
chain, reconstructs occurrence state, and resumes only at an allowed boundary.
A corrupt or missing event chain fails closed; a projection cannot fill the gap.

## Snapshots and projections

Immutable runtime snapshots accelerate recovery but are derived from an exact
event-log head. A snapshot records its source head, source ordinal, core run and
state identities, active occurrences, and contract version.

A mutable current pointer may identify the latest verified snapshot. Losing or
corrupting the pointer cannot destroy history; it is rebuilt from events.

SQLite is limited to disposable local read projections under the accepted
architecture. It is not the historical event authority. This proposal does not
select the authoritative event-store implementation. Every SQLite projection
must be rebuildable from verified events and snapshots.

## Artifact-reference verification

The runtime may ask an owning artifact store to verify identity, digest,
availability, and declared media or schema metadata. Verification returns a
bounded evidence reference. The runtime never stores source bytes, transcript
text, full chapter maps, credentials, private paths, or protected excerpts.

Artifact existence does not establish extraction quality, review acceptance,
scientific validity, rights clearance, lifecycle activation, or publication
authority.

## Baseline deterministic adapter

WF.2 retains an engine-neutral baseline planner and adapter path. It consumes
only supplied references, produces bounded plans and core adapter evidence, and
requires no CPN types or kernel.

The baseline path is the authoritative comparison path during future CPN shadow
replay. CPN enablement, equality, or promotion cannot weaken baseline checks or
remove baseline rollback.

## Dry run

A dry run executes structural preflight, owning-policy authority inspection in
non-granting mode, and deterministic planning. It performs no claim, dispatch,
external effect, final transition, current-pointer update, or lifecycle action.

Dry-run output is a bounded proposal bound to exact inputs and configuration. It
is not execution evidence and cannot be supplied as a successful worker result.

## Privacy and logging

Events, logs, exceptions, projections, and public task records contain compact
typed references only. They exclude:

- artifact payloads and source excerpts;
- PDF or transcript content;
- full chapter maps;
- credentials and authorization secrets;
- private or machine-specific paths;
- private workflow payload bodies; and
- mutable GitHub state copied as runtime authority.

Operational diagnostics use bounded reason codes and sanitized messages. Exact
protected evidence remains in its owning store.

## Replay

Semantic replay verifies the event predecessor chain and recomputes:

- idempotency decisions;
- occurrence state;
- deterministic plan identities from retained planning inputs;
- core transition outcomes from retained final inputs;
- immutable snapshots; and
- disposable read projections.

Replay never calls workers, external systems, clocks, random sources, artifact
payload readers, or CPN execution. External results are supplied as retained
evidence. Byte-identical serialization remains deferred to a future accepted
wire contract.

## Synthetic conformance vectors

Before runtime implementation, synthetic fixtures must define expected retained
events and prohibited calls for at least:

1. valid preflight and deterministic plan;
2. stale revision rejected before planning;
3. unknown operation rejected before planning;
4. terminal run rejected before planning;
5. structurally mismatched authority rejected before planning;
6. externally invalid, expired, or revoked authority rejected before dispatch;
7. identical request retry returning retained state;
8. changed idempotency reuse failing closed;
9. conflicting concurrent append;
10. duplicate worker claim;
11. lease expiry followed by reconciliation, not execution;
12. crash at each recovery-matrix boundary;
13. known-not-applied bounded retry;
14. ambiguous timeout blocking retry;
15. reconciliation confirming applied and confirming not applied;
16. final evidence mismatch rejected by the core;
17. retained outcome with stale pointer;
18. full projection rebuild;
19. corrupt event-chain detection;
20. aggregate core bounds exceeded;
21. privacy-safe diagnostic output; and
22. baseline operation with no CPN package involvement.

Fixtures use synthetic identities and payload-free references. Private documents
may supplement later operational validation but never enter Git or public logs.

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

The following decisions remain outside this proposal and must be accepted before
implementation where applicable:

- authoritative event serialization and schema migration;
- concrete event-store and snapshot storage technology;
- configured data-root resolution and filesystem hardening;
- clock source, lease duration, and operational scheduling;
- deployment-adapter code ownership;
- retention, archival, and backup policy;
- public wire compatibility;
- API and browser contracts; and
- release and migration policy.

## Acceptance gates

Runtime implementation remains blocked until:

- this contract is reviewed and accepted for an implementation slice;
- workflow-core consumer fit has no unresolved blocking finding;
- exact runtime identity domains and bounds are specified;
- synthetic conformance and crash fixtures are reviewed;
- the first deployment adapter declares idempotency and reconciliation
  capability;
- persistence authority and recovery behavior are accepted;
- privacy review confirms payload-free runtime state; and
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
- implementation, release, migration, or CPN promotion would begin without
  separate authorization.

## Consequences

- WF.2 can be reviewed as a consumer before runtime code exists.
- External effects remain outside pure core processing and deterministic
  planning.
- Ambiguous failures become explicit reconciliation states rather than retries.
- Append-only history remains recoverable independently of disposable views.
- The runtime carries additional records for plans, occurrences, claims,
  execution, and reconciliation.
- Exact serialization and persistence choices remain intentionally deferred.

[workflow-tracks-adr]:
  https://github.com/eragasa/projectkoios/blob/main/docs/adr.20260920.workflow-and-cpn-development-tracks.md
[workflow-runtime-task]:
  https://github.com/eragasa/projectkoios-workflow/issues/3
