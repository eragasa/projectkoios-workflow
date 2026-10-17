# Pure firing foundations

## Objective

Establish the authoritative representation, reservation, input-admission, and
plan records required before Workflow constructs an authoritative SDK request or
invokes the runtime engine for one pure external firing.

This task makes the existing experimental request and output mapping candidates
usable as part of an exact runtime chain. It does not by itself accept the
proposed canonical CPN-bindings contract set.

## Priority after the QE comparison

The bounded chain is sufficient for current QE value evidence. Remaining
complete-plan and profile work is not immediate infrastructure work; close only
the gaps required by the canonical durable path, a second owner, or an accepted
supported-release target. It is not a prerequisite for preserving Simulations'
existing domain workflow architecture.

## Required work

- [x] Establish one versioned Workflow-owned selected-binding adapter profile for
  the candidate SDK request boundary.
- [ ] Retain that exact adapter-profile identity with selection, request,
  persistence, and replay evidence rather than inferring it from a digest.
- [x] Treat the shadow kernel's internal identity preimages as provenance-bound
  backend evidence, not as public representations to duplicate or silently
  rewrite.
- [x] Define an immutable experimental reserved pure-action invocation that
  transitively binds the exact plan, deployment binding, definition,
  transition, enablement/selection evidence, selected binding, SDK request,
  predecessor marking/revision, occurrence, and attempt, with
  [local evidence](pure_action_reservation_evidence.md).
- [x] Bind every structurally admitted SDK input to the exact invocation
  candidate and explicit opaque source evidence through a content-identified
  input-mapping descriptor, with
  [local evidence](pure_action_input_admission_evidence.md). A nominal
  owner/source authority boundary now resolves and revalidates those references,
  with [local evidence](pure_action_input_authority_evidence.md). Simulations now
  supplies an outward content-addressed adapter candidate with
  [real-owner evidence](simulations/qe_artifact_set_durable_vertical_slice_evidence.md);
  release packaging and a production authority guarantee remain incomplete.
- [x] Prevent the reservation service from independently combining an arbitrary
  selected binding, runtime coordinates, and otherwise valid owner inputs; it
  now accepts only the reconstructed admitted-input aggregate.
- [x] Retain the selected-binding representation profile and owner-result mapping
  descriptor through bounded experimental plan/linking candidates, with
  [local evidence](pure_action_plan_closure_evidence.md).
- [x] Invoke only the exact manifest-validated SDK firer after pre-invocation
  revalidation, revalidate again afterward, and map only a current success, with
  [local evidence](pure_action_invocation_evidence.md).
- [x] Bind canonical flat-definition bytes and a candidate execution profile to
  the input plan and reservation, with
  [local evidence](pure_action_cpn_plan_evidence.md).
- [x] Correlate a mapped outcome to that CPN plan, its exact selected-binding
  evidence, supplied predecessor marking, and reservation, then compute a pure
  CPN successor candidate with output-color validation, with
  [local evidence](pure_action_firing_evidence.md).
- [x] Atomically retain a compact commit identity, consume the reservation, and
  advance the current marking coordinate in the in-memory reference repository,
  with [local evidence](pure_action_atomic_commit_evidence.md).
- [x] Persist the complete compact commit, ordered admitted evidence references,
  reservation consumption, and successor coordinate in one purpose-built SQLite
  transaction, with reopen, rollback, corruption, concurrency, and process-crash
  [evidence](pure_action_durable_persistence_evidence.md).
- [x] Retain strict canonical identity-only committed-event bytes and reconstruct
  the compact commit and coordinates read-only without owner or CPN invocation,
  with [local evidence](pure_action_committed_replay_evidence.md). A bounded
  canonical transcript is now atomically and durably linked to the compact
  commit, supports exact CPN refiring, reconstructs reservation lifecycle, and
  reconstructs bounded committed safety state, with
  [durable replay](pure_action_durable_cpn_replay_evidence.md),
  [commit orchestration](pure_action_durable_cpn_commit_orchestration_evidence.md),
  [lifecycle](pure_action_reservation_lifecycle_evidence.md), and
  [safety-state](pure_action_safety_state_replay_evidence.md) evidence. Complete
  global scheduler and runtime replay remain incomplete.
- [ ] Embed those candidates in the complete authoritative
  `WorkflowExecutionPlan`.
- [ ] Require complete `WorkflowExecutionBindings` to verify the exact
  plan-selected identities without substituting semantic choices.
- [ ] Distinguish candidate, admitted, mapped, and committed runtime records so
  that nominal type membership or direct construction grants no admission
  authority.
- [ ] Bind every behavior-affecting bound, decoder rule, and representation rule
  to a retained profile identity. Bounded definition and marking reconstruction
  primitives now have [local evidence](canonical_cpn_representation_decoding_evidence.md),
  but the complete execution-profile closure remains incomplete.

## Required tests

- [x] Reject a binding not selected by the retained selection result.
- [x] Reject owner inputs not correlated with the reserved invocation candidate.
- [x] Reject substituted definition, transition, predecessor, occurrence,
  attempt, mapping, source, and representation-profile identities across the
  selected-binding, request, input-admission, and reservation candidates.
- [x] Reject a stale predecessor revision before owner invocation and during
  the bounded post-owner revalidation candidate.
- [x] Reject direct reconstruction that substitutes payloads or identities in an
  admitted-stage record.
- [x] Prove that a behavior-affecting input-mapping profile mutation cannot reuse
  the previous input-extended plan identity. Complete authoritative plan
  identity remains gated.
- [x] Demonstrate deterministic request construction from the same retained
  evidence.
- [x] Preserve owner rejection, owner failure, worker mismatch, invocation
  exception, post-invocation staleness, and mapping rejection without firing.

## Completion evidence

- [x] Record exact Workflow and SDK revisions in the
  [QE adversarial coverage matrix](simulations/qe_pure_firing_adversarial_matrix.md).
- [x] Retain canonical selected-binding representation vectors and their profile
  identity in the
  [selected-binding evidence follow-up](selected_binding_evidence_followup.md).
- [x] Retain the execution-plan and deployment-binding identities in the
  reservation lifecycle and assert their exact QE fixture values after reopen.
- [x] Retain adversarial test results for selection, reservation, input
  provenance, profile, and reconstruction failures in the
  [coverage matrix](simulations/qe_pure_firing_adversarial_matrix.md).
- [x] Document the exact record that crosses each stage of the pure-firing
  runtime chain in that matrix.

The current
[experimental request-and-output mapping evidence](experimental_ascii_output_mapping_evidence.md),
its [selected-binding evidence follow-up](selected_binding_evidence_followup.md),
the [pure-action plan-closure evidence](pure_action_plan_closure_evidence.md),
the [pure-action reservation evidence](pure_action_reservation_evidence.md),
the [pure-action input-admission evidence](pure_action_input_admission_evidence.md),
the [pure-action input-authority evidence](pure_action_input_authority_evidence.md),
the [pure-action invocation evidence](pure_action_invocation_evidence.md),
the [pure-action CPN plan-closure evidence](pure_action_cpn_plan_evidence.md),
the [pure-action CPN firing evidence](pure_action_firing_evidence.md),
the [pure-action atomic-commit evidence](pure_action_atomic_commit_evidence.md),
the [pure-action durable-persistence evidence](pure_action_durable_persistence_evidence.md),
the [pure-action committed-replay evidence](pure_action_committed_replay_evidence.md),
the [canonical CPN representation decoding evidence](canonical_cpn_representation_decoding_evidence.md),
the [pure-action CPN refiring evidence](pure_action_cpn_refiring_evidence.md),
the [real-owner QE durable vertical slice](simulations/qe_artifact_set_durable_vertical_slice_evidence.md),
and the [QE adversarial coverage matrix](simulations/qe_pure_firing_adversarial_matrix.md)
are candidate evidence for this task. Together they still do not supply complete
plan/profile closure, released owner/runtime packaging, a structurally
independent second owner, or authoritative global replay.

## Exclusions

The shadow CPN production source and transformed tests remain byte-identical to
the revision recorded in `provenance/colored-petri-net-shadow.json`. This task
must not change that source merely to fit the adapter profile; replacing or
migrating the shadow requires separate accepted ownership and provenance
evidence.

The foundations task does not itself authorize effects, owner-domain parsing by
Workflow, acceptance of the complete proposed CPN-bindings contract set,
replacement of the provenance-bound shadow, or production use. Its candidates
are exercised by a separately recorded bounded pure-firing vertical slice.
