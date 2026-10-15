# Technical-debt tasks

This directory indexes bounded cleanup and maintainability work in
`projectkoios-workflow`.

Technical-debt records must state the current defect or cost, affected scope,
validation required, and the condition that makes the work actionable. They do
not authorize unrelated refactoring or change contract status.

## Tasks

- [Remove private Workflow SDK contract duplicates](remove_private_sdk_contract_duplicates.md)
  after an accepted SDK alpha surface exists.
- [Consolidate pure-action validation](consolidate_pure_action_validation.md)
  after admission-stage records stabilize or before the path enters a runtime
  hot loop. The completed internal-organization slice has separate
  [evidence](pure_action_internal_organization_evidence.md).
- [Consolidate the private SQLite persistence boundary](consolidate_sqlite_private_database_boundary.md)
  before adding durable CPN replay transcripts, another SQLite adapter, or a
  schema migration.
- [Retire the experimental pure-action surface](retire_experimental_action_surface.md)
  before broader SDK adoption or supported pure external firing.
