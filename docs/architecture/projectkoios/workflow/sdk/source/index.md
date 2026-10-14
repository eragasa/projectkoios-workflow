# `projectkoios.workflow.sdk.source` architecture

## Responsibility

The source module defines the external authoring language from which immutable generic workflow definitions are constructed. Its principal nominal owners are `AbstractWorkflow` and `AbstractTask`.

Source owners declare stable identities, immutable composition, route kind, action contracts, and nested targets. They execute nothing during compilation. Final base-class properties lower owner declarations to generic frozen records so each concrete workflow does not invent a new definition schema.
