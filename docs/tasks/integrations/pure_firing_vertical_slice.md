# Pure firing vertical slice

## Objective

Prove one complete effect-free path through an external owner integration and
the authoritative CPN runtime:

```text
CPN selected binding
→ SDK firing request
→ consumer-owned firer
→ correlated SDK result
→ admitted external output binding
→ CPN firing
→ retained successor marking and history
```

## Required work

- [ ] Pass the [pure-firing foundations gate](pure_firing_foundations.md).
- [x] Construct one exact transition-to-firer binding through the bounded
  experimental execution-plan candidate.
- [x] Reserve the exact selected occurrence against the current predecessor
  marking and revision.
- [x] Create the firing request only from the reserved invocation and its admitted
  owner inputs.
- [x] Invoke a consumer-owned integration through the SDK `Firer` ABC.
- [x] Revalidate and consume the reservation exactly once after the owner result
  returns.
- [x] Reject changed occurrence, attempt, binding, request, descriptor, result,
  predecessor, profile, or input-provenance correlation.
- [x] Map admitted owner output to an explicit external-output binding.
- [x] Validate the mapped external value against the transition output color.
- [x] Invoke the pure CPN transition firer only after current-state result
  admission.
- [x] Atomically retain compact commit identities, admitted evidence references,
  CPN replay evidence, lifecycle transition, consumed reservation, and successor
  marking without retaining owner payload bodies or private locators.
- [x] Prove rollback leaves no partially committed occurrence or successor, with
  [durable-persistence evidence](pure_action_durable_persistence_evidence.md).
- [x] Replay the committed firing through the retained experimental CPN profile;
  complete global behavior-profile closure remains a foundations gate.

The first intended consumer fixture is the
[Simulations QE artifact-set pilot](simulations/qe_artifact_set_sdk_pilot.md).
The bounded path now proves selective durability value; it does not justify
replacing Simulations' typed SCF facade or local SNAKES lifecycle. That adoption
boundary is tracked explicitly in
[selective runtime adoption](simulations/selective_runtime_adoption.md).
Its owner-side SDK boundary and isolated cross-wheel firing now pass, but it
correctly stops at a correlated SDK result. The SDK
[transition action binding](../../architecture/projectkoios/workflow/sdk/actions/TransitionActionBinding/)
uses the Simulations-owned `artifact_set_identity` as the opaque CPN string
output and retains the complete canonical `artifact_set` document as evidence;
the transport payload digest remains integrity evidence rather than domain
state. An experimental Workflow-owned selected-binding evidence record now
requires an exact successful enablement and selection pair, proves membership of
the selected binding in the enabled set, and retains the adapter-profile
identity, canonical bytes, and derived digest. The request factory consumes that
evidence rather than a bare binding and constructs the SDK request without
accepting a claimed digest. The later authority and reservation candidates now
require request inputs to come from the exact owner/source repository
observations selected by the retained plan.
Bounded experimental plan/linking candidates now retain the representation
profile and output mapping and verify the exact firer against an SDK integration
manifest. A bounded experimental reservation candidate now constructs the
plan-selected SDK request and content-identifies its exact plan, deployment,
selection, request, predecessor, occurrence, and attempt context before
atomically reserving the current predecessor. Its non-durable in-memory
repository rejects stale and concurrent conflicting attempts and supports
post-owner current-state revalidation. An input-extended plan now selects one
opaque source kind and profile per SDK role; a structural admission aggregate
binds exact source evidence and request bytes, and the reservation service no
longer accepts raw input tuples. A nominal owner/source repository now resolves
opaque references with closed uncertainty outcomes; reservation reloads and
compares the exact source observation. Simulations now supplies an outward
content-addressed owner adapter candidate, while release packaging and its
production authority guarantee remain open. Reservation consumption is exposed
only inside the accepted atomic firing boundary. A bounded v0 invocation
candidate now performs both revalidation phases, validates the live worker
against the retained manifest, invokes the exact SDK firer, preserves closed
non-success and exceptional outcomes, and maps only a current SDK success. A
bounded v0 CPN plan extension now binds canonical definition bytes and an exact
candidate execution profile into the reservation. The CPN firing candidate
correlates the mapped outcome with that plan, the exact selection, supplied
byte-equal definition, supplied predecessor marking, and active reservation; the
provenance-bound pure firer validates output color and computes a candidate
successor and audit. A bounded in-memory atomic-commit candidate now consumes
that exact reservation and advances the authoritative marking coordinate under
one lock while retaining a compact content commitment. A purpose-built SQLite
candidate now retains the complete compact commit fields, ordered source
authority references, reservation consumption, and successor coordinate in one
durable transaction, with reopen, process-crash, rollback, corruption, and
concurrency evidence. These candidates are not the complete authoritative plan
or deployment bindings. Canonical identity-only event bytes and compact
read-only reconstruction now exist. Bounded canonical definition and semantic
marking reconstruction primitives also exist. Canonical CPN transcript evidence
is durably linked within the same commit, exact refiring is available, lifecycle
history is reconstructable, and bounded committed safety-state replay correlates
both markings without owner invocation.

The paired mapper validates the exact SDK descriptors, retained context, result
metadata, canonical ASCII identity, and evidence order, then constructs one
declared candidate shadow-CPN `STRING` binding. Neither component expands the
standalone SDK, grants runtime admission authority, or claims the proposed full
CPN-bindings contract. The
[pure-firing foundations task](pure_firing_foundations.md) must still close the
complete representation-profile and execution-plan semantics before this
bounded path can claim the authoritative global runtime or CPN-bindings
contract. The current Workflow-owned execution services already perform
predecessor/source revalidation, result admission, pure firing, and atomic
retention for this slice. No SDK record authorizes inventing the mapping inside
the owner adapter.

## Completion evidence

- [x] Record the isolated candidate
  [experimental request-and-output mapping evidence](experimental_ascii_output_mapping_evidence.md),
  [selected-binding evidence follow-up](selected_binding_evidence_followup.md),
  [pure-action plan-closure evidence](pure_action_plan_closure_evidence.md),
  [pure-action reservation evidence](pure_action_reservation_evidence.md),
  [pure-action input-admission evidence](pure_action_input_admission_evidence.md),
  [pure-action input-authority evidence](pure_action_input_authority_evidence.md),
  [pure-action invocation evidence](pure_action_invocation_evidence.md),
  [pure-action CPN plan-closure evidence](pure_action_cpn_plan_evidence.md),
  [pure-action CPN firing evidence](pure_action_firing_evidence.md),
  [pure-action atomic-commit evidence](pure_action_atomic_commit_evidence.md),
  [pure-action durable-persistence evidence](pure_action_durable_persistence_evidence.md),
  [pure-action committed-replay evidence](pure_action_committed_replay_evidence.md),
  [canonical CPN representation decoding evidence](canonical_cpn_representation_decoding_evidence.md),
  [pure-action CPN refiring evidence](pure_action_cpn_refiring_evidence.md), and
  [real-owner QE durable vertical-slice evidence](simulations/qe_artifact_set_durable_vertical_slice_evidence.md).
- [x] Record exact committed SDK, Workflow runtime, and consumer revisions for
  the complete bounded slice, including reproducible wheel digests.
- [x] Retain request, result, reservation, profile, binding, firing, and history
  identities.
- [x] Retain deterministic replay evidence.
- [x] Retain negative test results for stale and mismatched results, stale
  reservations, invalid input provenance, partial-write rollback, and replay
  profile substitution.
- [x] Prove the consumer firer receives only the canonical SDK request copy, not
  the Workflow marking object, and cannot mutate authoritative marking state.

## Exclusions

The slice performs no filesystem staging, process launch, scheduler submission,
network call, retry, reconciliation, calculator execution, or production
migration.
