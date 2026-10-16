# `projectkoios.workflow.compilation` architecture

## Responsibility

Compilation converts external immutable Task/Workflow definitions into complete
content-addressed execution plans and separately links those plans to exact
deployments. It prevents mutable owners, handlers, providers, and runtime
objects from entering declarative state.

A Workflow compiles to one flat canonical CPN plan. Atomic Task instances map to
pure or lifecycle transition routes. Workflow-backed Task instances retain exact
references to separately compiled child plans and terminal-delivery contracts;
child topology is never flattened into the parent net.

Compilation and linking fire no transition, create no run, invoke no Task, and
perform no owner effect.
