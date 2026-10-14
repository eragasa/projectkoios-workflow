# `AbstractWorkflow` implementation

## Responsibility

Provide abstract `identity` and `composition` declarations and a non-overridable definition constructor that validates exact built-in record types and derives the content identity. Avoid mutable caches and provider lookup.

Migration evidence is the historical class in `ksdft2effmass` commit `5210b760...`. The target definition replaces the earlier task/gate executable model with fragment composition compiled to canonical flat CPN IR. Conformance must cover identity stability, subclass misuse, post-compilation mutation, and owning-workflow self-target rejection.
