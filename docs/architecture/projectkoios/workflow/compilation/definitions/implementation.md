# `projectkoios.workflow.compilation.definitions` implementation

## Responsibility

Use frozen slotted closed records with strict built-in type validation, bounded
collections, canonical tuple order, schema/compiler versions, and content
identities. The discriminated definition model must make atomic and composite
Task shapes impossible to confuse.

An atomic definition contains exactly one route descriptor. A Workflow definition
contains immutable Task-instance composition and child contracts, not an atomic
route. A workflow-backed Task references a separate Workflow definition and
never embeds a live owner or child CPN graph.

Canonical decoding rejects unknown fields, arbitrary subclasses, route/composition
mixtures, direct or indirect cycles, and identity/content disagreement. Existing
experimental pure-action plan records remain unchanged compatibility evidence.
