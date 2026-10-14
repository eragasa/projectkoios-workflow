# `projectkoios.workflow.compilation.planning` implementation

## Responsibility

Adapt historical `planning.py`, blob `9a5117aeedcdbc1cbd6fb799c5b39e9dbbc425a4`, and Frankenstein composition rules. The constructor must return either one complete plan or closed findings; it must never return a plan with unresolved ports, targets, mappings, or priorities.

Plans are serialized canonically and content-addressed. Live source owners and provider bindings are forbidden fields and must be detected by construction-time type closure rather than convention alone.
