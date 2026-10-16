# Integration tasks

This directory indexes work that integrates Workflow-owned contracts and
runtime behavior with external owner repositories.

Integration tasks must preserve owner boundaries, identify the exact contract
and version under evaluation, and distinguish fixture review from adoption of a
runtime dependency.

## Integration sequence

1. [Workflow SDK alpha consumption readiness](sdk_alpha_readiness.md)
2. [Simulations owner-side SDK pilot](simulations/)
3. [Pure-firing foundations](pure_firing_foundations.md), informed by the
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
   [pure-action CPN refiring evidence](pure_action_cpn_refiring_evidence.md),
   [durable CPN replay evidence](pure_action_durable_cpn_replay_evidence.md),
   [durable CPN commit orchestration evidence](pure_action_durable_cpn_commit_orchestration_evidence.md),
   and [reservation lifecycle evidence](pure_action_reservation_lifecycle_evidence.md)
4. [Pure-firing vertical slice](pure_firing_vertical_slice.md)
5. [Second owner SDK pilot](second_owner_pilot.md)
6. [Broader SDK adoption gate](broader_adoption_gate.md)
7. [Effectful integration gate](effectful_integration_gate.md)

The first two tasks establish a usable SDK boundary and one owner fixture. The
foundations task closes representation, reservation, input-provenance, and plan
semantics before the vertical slice claims one authoritative pure CPN path. The
second owner then tests generality. Broader adoption and external effects remain
separately gated.
