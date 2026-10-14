# Integration tasks

This directory indexes work that integrates Workflow-owned contracts and
runtime behavior with external owner repositories.

Integration tasks must preserve owner boundaries, identify the exact contract
and version under evaluation, and distinguish fixture review from adoption of a
runtime dependency.

## Integration sequence

1. [Workflow SDK alpha consumption readiness](sdk_alpha_readiness.md)
2. [Pure firing vertical slice](pure_firing_vertical_slice.md), including the
   [experimental ASCII output-mapping evidence](experimental_ascii_output_mapping_evidence.md)
3. [Simulations pilot](simulations/)
4. [Second owner SDK pilot](second_owner_pilot.md)
5. [Broader SDK adoption gate](broader_adoption_gate.md)
6. [Effectful integration gate](effectful_integration_gate.md)

The first two tasks establish a usable SDK boundary and one complete pure CPN
path. The second owner tests generality. Broader adoption and external effects
remain separately gated.
