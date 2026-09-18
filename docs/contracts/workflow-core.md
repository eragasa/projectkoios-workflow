# Petri-independent workflow core contract

## Status

Proposed under
[`WORKFLOW-CORE-01`](https://github.com/eragasa/projectkoios-workflow/issues/1).
This document is a planning contract. It does not authorize implementation,
production transfer, consumer migration, release, deprecation, or source
removal.

## Purpose

The workflow core defines the smallest reusable vocabulary needed to describe
and audit workflow state changes without depending on a colored-Petri-net
representation, scheduler, persistence engine, user interface, external
executor, or scientific application.

The existing colored-Petri-net package remains a non-authoritative backend
shadow. The core is not a renamed copy of `ksdft2effmass.workflows.model`, and
the shadow kernel is not changed merely to fit this proposal.

## Design principles

The core is:

- immutable at its domain boundaries;
- deterministic for pure validation and state-transition functions;
- fail-closed for invalid identities, revisions, and references;
- explicit about authority and human decisions;
- independent of storage and transport;
- independent of execution formalism; and
- unable to perform scientific calculations or external effects.

The core describes evidence about state change. It does not make an operation
safe, scientifically valid, or authorized merely because a transition is
structurally enabled.

## Conceptual records

Names remain subject to implementation review, but the core must represent the
following concepts without backend types.

### Workflow definition reference

A definition reference identifies one immutable workflow contract and version.
It contains no executable callable, database handle, Petri marking, or UI
configuration.

Its identity binds the stable definition content required by the core. An
adapter may bind additional engine-specific definition identities separately.

### Workflow run

A run identifies one attempt to apply a workflow definition to an explicitly
identified subject or project context. It records:

- run identity;
- definition identity;
- subject identity without importing the subject's domain model;
- current immutable state identity;
- monotonic revision or equivalent concurrency evidence;
- parent or predecessor run identity when applicable;
- status and terminal reason;
- artifact and decision references; and
- contract version.

A run does not own the scientific object, source artifact, or external process
that it references.

### State snapshot

A state snapshot is immutable and content-identified. It contains only bounded,
engine-neutral state needed by the core and opaque typed references owned by
adapters or applications.

The core does not define a Petri marking as its universal state model. A Petri
adapter may associate a marking identity and evidence with a core snapshot.

### Transition request

A transition request records a proposed state change with:

- request identity;
- run and expected prior-revision identity;
- operation or transition intent identity;
- ordered input and artifact references;
- actor or initiating-agent reference;
- authority evidence reference;
- idempotency identity where applicable;
- request bounds and contract version; and
- no embedded executable code.

A request is not authorization. It is invalid when required authority evidence
is absent, mismatched, expired under the owning policy, or outside the
operation's declared scope.

### Transition outcome

A transition outcome distinguishes at least:

- applied;
- rejected as invalid;
- not enabled under the selected adapter;
- conflict with the expected prior revision;
- blocked pending an external or human decision; and
- infrastructure failure outside the pure core.

An applied outcome retains request, prior-state, successor-state, validation,
artifact, decision, and adapter-evidence identities. A rejected or blocked
outcome retains structured reasons without manufacturing a successor state.

Infrastructure failure must not be represented as a valid business rejection
or human decision.

### Artifact reference

An artifact reference is a typed immutable locator and digest owned by an
external artifact domain. The core records identity, kind, provenance link, and
role in a transition. It does not embed large artifact payloads or reinterpret
artifact content.

Generated, observed, accepted, and published artifacts remain distinguishable.
Reference by a workflow does not grant acceptance or publication authority.

### Decision reference

A decision reference identifies a separately recorded human, architecture,
scientific, review, or operational decision. It records decision kind, scope,
subject, authority, outcome, evidence identity, and version.

The core does not collapse technical validation, review disposition, operator
authorization, lifecycle acceptance, and scientific acceptance into one flag.

### Audit event

An audit event records a bounded immutable observation about request,
validation, transition, artifact, or decision processing. Events have stable
ordering evidence within a run but do not require the core to choose a database
or event-log technology.

## Identity and nominality

Identities are nominal and typed. Definition, run, state, request, outcome,
artifact, decision, and event identities are not interchangeable even when
their serialized values match.

Stable identity binds semantic content and contract version. It excludes
process-local addresses, mutable timestamps used only for display, filesystem
paths, and storage-assigned row numbers.

The shadow's retained `ksdft2effmass.petrinet.colored.*` identity-domain strings
are backend conformance evidence. They are not core identities or an accepted
wire contract.

Public identity domains and migration rules remain deferred to
`WORKFLOW-IDENTITY-WIRE-01`.

## Pure transition boundary

The core may expose pure operations that:

1. validate a definition reference, run, snapshot, and request;
2. verify expected revision and bounded references;
3. delegate engine-specific enablement and successor-state calculation through
   a later adapter boundary;
4. validate the returned adapter evidence;
5. produce an immutable outcome and audit evidence; and
6. leave persistence and effects to outer layers.

The core itself does not:

- select a Petri transition or binding;
- invoke tools, calculators, schedulers, or external services;
- read or write a database;
- mutate a run in place;
- poll infrastructure;
- decide scientific acceptance; or
- publish artifacts.

## Adapter boundary

An engine adapter will translate between core references and one engine's
immutable definition and state evidence. Adapter input and output are explicit,
bounded, and testable. The adapter cannot grant authority unavailable in the
core request or owning application policy.

The colored-Petri-net adapter is a future task. It must preserve the existing
kernel's pure definition, validation, enablement, selection, firing, and audit
behavior without importing core or application policy into the kernel.

Managed-project adapters remain separate from engine adapters. A scientific
project owns the mapping from its artifacts, calculations, and decisions to the
core vocabulary.

## Validation and failure

Validation is deterministic and accumulates stable typed findings subject to
explicit bounds. Invalid input fails closed without repair or partial state
mutation.

At minimum validation covers:

- supported contract versions;
- nominal identity domains;
- complete required fields;
- finite collection and payload bounds;
- reference integrity;
- expected-revision conflicts;
- duplicate identities;
- terminal-run behavior;
- authority-evidence presence; and
- adapter-output consistency when adapter evidence is supplied.

A structurally valid request may still be unauthorized, disabled by an
adapter, blocked by a human decision, or rejected by an application policy.

## Replay and determinism

Given identical validated core input and identical adapter evidence, pure core
processing produces byte-equivalent canonical data and the same stable
identities. Replay verifies prior outcomes without reperforming external effects
or silently upgrading contract versions.

Wall-clock observations, random values, external responses, and human decisions
enter only as explicitly identified evidence supplied to the pure boundary.
They are not generated implicitly during replay.

## Dependency direction

The core may depend only on the Python standard library and explicitly accepted
Project Koios foundation contracts that remain independent of workflow
backends, persistence, UI, adapters, and applications.

The following dependencies point inward through protocols or data references,
never outward imports from the core:

```text
UI / API / CLI
runtime and persistence
external execution adapters
managed-project adapters
engine adapters
        ↓
workflow core
```

The colored-Petri-net kernel remains a sibling backend and does not import the
core:

```text
workflow core ← core-to-Petri adapter → colored-Petri backend
```

Dependency-direction tests enforce these boundaries.

## Serialization boundary

Internal core records use frozen dataclasses or ordinary immutable domain
classes. A public wire format is not selected by this task.

Any temporary boundary serializer is versioned, rejects unknown fields,
enforces resource bounds before constructing domain objects, and makes no
compatibility promise beyond its documented scope.

## Acceptance evidence

`WORKFLOW-CORE-01` is ready for architecture acceptance when the contract and
prototype tests demonstrate:

- no dependency on Petri-net or application types;
- nominal and deterministic identity behavior;
- immutable state and outcomes;
- fail-closed validation and expected-revision conflicts;
- explicit separation of technical, authorization, lifecycle, and scientific
  decisions;
- deterministic replay using supplied adapter evidence;
- dependency-direction enforcement;
- bounded construction and serialization; and
- full unit, lint, type, build, and isolated-install validation.

Passing these checks does not authorize production transfer or establish
consumer compatibility.

## Deferred decisions

This contract does not select:

- the public wire format or compatibility duration;
- a persistence or event-store implementation;
- a scheduler or dispatch model;
- the colored-Petri adapter;
- a managed-project adapter;
- consumer migration or shadow-replay thresholds;
- release and rollback procedures; or
- deprecation and removal of the source implementation.
