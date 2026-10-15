# Pure firing foundations

## Objective

Establish the authoritative representation, reservation, input-admission, and
plan records required before Workflow constructs an authoritative SDK request or
invokes the runtime engine for one pure external firing.

This task makes the existing experimental request and output mapping candidates
usable as part of an exact runtime chain. It does not by itself accept the
proposed canonical CPN-bindings contract set.

## Required work

- [x] Establish one versioned Workflow-owned selected-binding adapter profile for
  the candidate SDK request boundary.
- [ ] Retain that exact adapter-profile identity with selection, request,
  persistence, and replay evidence rather than inferring it from a digest.
- [x] Treat the shadow kernel's internal identity preimages as provenance-bound
  backend evidence, not as public representations to duplicate or silently
  rewrite.
- [ ] Define an immutable reserved pure-action invocation, or equivalent accepted
  records, that binds the exact definition, transition, enablement result,
  selection result, predecessor marking and revision, selected binding,
  occurrence, and attempt.
- [ ] Bind every admitted SDK input to that reserved invocation and to explicit
  source evidence through a content-identified input-mapping descriptor.
- [ ] Prevent callers from independently combining an arbitrary selected binding,
  runtime coordinates, and otherwise valid owner inputs.
- [x] Retain the selected-binding representation profile and owner-result mapping
  descriptor through bounded experimental plan/linking candidates, with
  [local evidence](pure_action_plan_closure_evidence.md).
- [ ] Embed those candidates in the complete authoritative
  `WorkflowExecutionPlan`.
- [ ] Require complete `WorkflowExecutionBindings` to verify the exact
  plan-selected identities without substituting semantic choices.
- [ ] Distinguish candidate, admitted, mapped, and committed runtime records so
  that nominal type membership or direct construction grants no admission
  authority.
- [ ] Bind every behavior-affecting bound, decoder rule, and representation rule
  to a retained profile identity.

## Required tests

- [x] Reject a binding not selected by the retained selection result.
- [ ] Reject owner inputs not correlated with the reserved invocation.
- [ ] Reject substituted definition, transition, predecessor, occurrence,
  attempt, mapping, and representation-profile identities.
- [ ] Reject a stale predecessor revision before owner invocation and after an
  owner result returns.
- [ ] Reject direct reconstruction that substitutes payloads or identities in an
  admitted-stage record.
- [ ] Prove that a behavior-affecting profile mutation cannot reuse the previous
  authoritative plan identity.
- [x] Demonstrate deterministic request construction from the same retained
  evidence.

## Completion evidence

- [ ] Record exact Workflow and SDK revisions.
- [x] Retain canonical selected-binding representation vectors and their profile
  identity in the
  [selected-binding evidence follow-up](selected_binding_evidence_followup.md).
- [ ] Retain the execution-plan and deployment-binding identities.
- [ ] Retain adversarial test results for selection, reservation, input
  provenance, profile, and reconstruction failures.
- [ ] Document the exact record that crosses each stage of the pure-firing
  runtime chain.

The current
[experimental request-and-output mapping evidence](experimental_ascii_output_mapping_evidence.md),
its [selected-binding evidence follow-up](selected_binding_evidence_followup.md),
and the [pure-action plan-closure evidence](pure_action_plan_closure_evidence.md)
are candidate evidence for this task. They do not satisfy the reservation,
input-provenance, complete plan closure, persistence, or authoritative replay
requirements above.

## Exclusions

The shadow CPN production source and transformed tests remain byte-identical to
the revision recorded in `provenance/colored-petri-net-shadow.json`. This task
must not change that source merely to fit the adapter profile; replacing or
migrating the shadow requires separate accepted ownership and provenance
evidence.

This task does not fire a CPN transition, mutate a marking, implement effects,
perform owner-domain parsing, accept the complete proposed CPN-bindings contract
set, replace the provenance-bound shadow, or authorize production use.
