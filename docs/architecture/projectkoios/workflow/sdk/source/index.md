# `projectkoios.workflow.sdk.source` architecture

> **Status: iteration-2 target; not part of SDK `0.1.0a1`.**

## Responsibility

The source module defines the nominal external authoring language from which
immutable generic Task and Workflow definitions are constructed. `Task` is the
parent-visible source abstraction. `Workflow` is a composite specialization of
`Task`.

A Workflow declares an immutable ordered composition of Task instances. An
atomic Task declares exactly one pure or effectful execution route. A
workflow-backed Task is represented by a Workflow definition and creates a
distinct child Workflow run when invoked by a parent.

Source owners execute nothing during compilation. Final non-overridable base
properties lower owner declarations to closed frozen definitions, so concrete
owners do not invent serialized schemas or retain live behavior in plans.

The existing document names `AbstractTask` and `AbstractWorkflow` are
provisional architecture names. Exact future SDK symbols remain gated on owner
evidence and compatibility review.
