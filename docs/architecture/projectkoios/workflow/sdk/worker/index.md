# `projectkoios.workflow.sdk.worker` architecture

## Responsibility

The SDK worker module defines how an external package groups its manifest, transition action bindings, and lifecycle providers for hosting by the generic worker process. It exposes implementation capabilities without exposing mutable CPN state.

The package-level worker plugin is not the persistent worker daemon and does not claim or schedule work by itself.
