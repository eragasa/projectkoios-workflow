# Integration tasks

This directory indexes work that integrates Workflow-owned contracts and
runtime behavior with external owner repositories.

Integration tasks must preserve owner boundaries, identify the exact contract
and version under evaluation, and distinguish fixture review from adoption of a
runtime dependency.

## Integration sequence

Completed evidence establishes the standalone SDK, the Simulations owner
boundary, and one bounded durable real-owner path. Current work should now
prioritize demonstrated value over further infrastructure.

1. Preserve the
   [selective Simulations adoption boundary](simulations/selective_runtime_adoption.md).
2. Complete the
   [canonical durable pure-action path](canonical_durable_pure_action_path.md).
3. Run the [second owner SDK pilot](second_owner_pilot.md) as an owner-side
   generality test.
4. Close the remaining [pure-firing foundations](pure_firing_foundations.md)
   only to the extent required for a supported two-owner pure path, informed by
   the
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
   [reservation lifecycle evidence](pure_action_reservation_lifecycle_evidence.md),
   and [committed safety-state replay evidence](pure_action_safety_state_replay_evidence.md).
5. Complete the remaining
   [pure-firing vertical-slice](pure_firing_vertical_slice.md) release and
   isolation gates; the bounded runtime path is already exercised by the
   [QE durable vertical-slice evidence](simulations/qe_artifact_set_durable_vertical_slice_evidence.md).
6. Pass the [broader SDK adoption gate](broader_adoption_gate.md).
7. Address the [effectful integration gate](effectful_integration_gate.md) only
   when an owner requests durable effect orchestration.

The existing Simulations lifecycle remains its current owner architecture.
Workflow's bounded QE path is an additive durability mechanism for one pure
action, not a general replacement. Global scheduler replay, additional replay
variants, and effect infrastructure remain deferred until owner evidence makes
them necessary.
