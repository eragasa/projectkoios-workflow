# `projectkoios.workflow.cpn.composition` implementation

## Responsibility

Implement from the Frankenstein CPN composition specifications with independent validation in Workflow. Reject incompatible colors, directions, multiplicity, unresolved ports, undeclared collisions, incomplete inheritance evidence, and ambiguous priority.

Retain a fragment-to-flat-identity map for provenance and visualization. The map must not affect kernel validation, enablement, selection, or firing.
