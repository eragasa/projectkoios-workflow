# `projectkoios.workflow.compilation.bindings` architecture

## Responsibility

The bindings module links one exact compiled execution plan to one complete, route-compatible deployment. It verifies action providers, lifecycle providers, worker environments, nested targets, and capability guarantees without modifying the plan.

Binding is distinct from registry discovery and from engine invocation. Its result prevents the engine from performing a second lookup or silently selecting another provider.
