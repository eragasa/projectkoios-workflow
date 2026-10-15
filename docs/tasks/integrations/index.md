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
   and [pure-action reservation evidence](pure_action_reservation_evidence.md)
4. [Pure-firing vertical slice](pure_firing_vertical_slice.md)
5. [Second owner SDK pilot](second_owner_pilot.md)
6. [Broader SDK adoption gate](broader_adoption_gate.md)
7. [Effectful integration gate](effectful_integration_gate.md)

The first two tasks establish a usable SDK boundary and one owner fixture. The
foundations task closes representation, reservation, input-provenance, and plan
semantics before the vertical slice claims one authoritative pure CPN path. The
second owner then tests generality. Broader adoption and external effects remain
separately gated.
