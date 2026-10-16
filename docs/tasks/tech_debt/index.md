# Technical-debt tasks

This directory indexes bounded cleanup and maintainability work in
`projectkoios-workflow`.

Technical-debt records must state the current defect or cost, affected scope,
validation required, and the condition that makes the work actionable. They do
not authorize unrelated refactoring or change contract status.

## Current priority

Do not start another internal-organization project merely to make the
experimental runtime more comprehensive. The next technical work is the bounded
[canonical durable pure-action path](../integrations/canonical_durable_pure_action_path.md),
followed by second-owner evidence.

## Deferred tasks

- [Remove private Workflow SDK contract duplicates](remove_private_sdk_contract_duplicates.md)
  only when a concrete duplicate blocks packaging or a second owner.
- [Retire the experimental pure-action surface](retire_experimental_action_surface.md)
  after the second-owner result and before broader SDK adoption or a supported
  pure external-firing declaration.

## Completed organization evidence

- [Pure-action internal organization](pure_action_internal_organization_evidence.md)
  records the completed validation and module split.
- [SQLite private-boundary consolidation](sqlite_private_boundary_consolidation_evidence.md)
  records the completed private database organization.
- [Durable-history internal organization](durable_history_internal_organization_evidence.md)
  records the completed replay and lifecycle module split.

The older planning documents remain as historical rationale; they are not
current authorization for further refactoring.
