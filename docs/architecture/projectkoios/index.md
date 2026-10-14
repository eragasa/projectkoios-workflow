# `projectkoios` namespace architecture

## Responsibility

The `projectkoios` architecture level defines dependencies shared by Project Koios packages. For this repository it establishes that Workflow consumes stable base action contracts while remaining independent of scientific, ingestion, reference, application, and simulation implementations.

The namespace may own accepted genuinely universal interoperability conventions such as immutable data objects and the `DataObjectActionRequest → DataObjectActionizer → DataObjectActionResult` operation shape. Whether source identity, source type, or source policy primitives are universal is a separate product-level review; Workflow must not define them by convenience or copy provisional owner models. It does not make the Workflow service a parent of every product package and does not grant domain authority.

Workflow-specific process semantics begin in the `workflow` child package. Accepted external value types can become exact token-color or action-contract inputs without transferring their semantics to Workflow. Domain packages implement or adapt to future Workflow SDK interfaces in their own distributions and are loaded only by isolated exporters or workers.
