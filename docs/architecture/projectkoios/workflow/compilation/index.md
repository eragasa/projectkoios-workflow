# `projectkoios.workflow.compilation` architecture

## Responsibility

Compilation converts external source-owner definitions into an immutable, complete, content-addressed execution plan and separately links that plan to one exact deployment. It is the boundary that prevents mutable adapters, providers, and runtime objects from entering declarative workflow state.

The compiler lowers fragment composition to canonical flat CPN IR. The linker proves that provider and nested-target bindings exactly match the compiled plan. Neither phase fires a transition or performs a domain effect.
