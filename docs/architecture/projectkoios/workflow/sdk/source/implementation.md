# `projectkoios.workflow.sdk.source` implementation

## Responsibility

Adapt the source-owner pattern from historical `ksdft2effmass/workflows/tasks.py` at commit `5210b760c6c13f9f5980a649f0a85362a26b5d2d`, blob `eb9b37542f0ab17cc2b33881b3882fc42c3ef8fd`.

The target may rename historical execution kinds, but it must preserve the distinction among pure typed actions, external lifecycle effects, and nested-net targets. Source definitions must be independent of mutable owner state after construction. Tests must mutate an owner after compilation and prove that the compiled plan is unchanged.
