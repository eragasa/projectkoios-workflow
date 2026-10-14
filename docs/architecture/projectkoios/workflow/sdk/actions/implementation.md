# `projectkoios.workflow.sdk.actions` implementation

## Responsibility

Provide a generic ABC and a validating base that enforce exact request/result types, action descriptor identity, occurrence correlation, schema bounds, and output-binding identity. The base may convert known provider protocol failures to closed records but must not translate arbitrary domain failures into success.

The compiler consumes explicit descriptor records and explicit source-definition connections. It may validate port/color compatibility and select a registered lowering template from the declared effect class. It must not inspect Python annotations or method bodies to invent places, arcs, guards, joins, retry, concurrency, acceptance, or child behavior. Reflection may locate a declared manifest in an isolated exporter; it is never workflow authoring.

The wire representation uses content-addressed typed envelopes. Large or private data remains in owner storage and is represented only by bounded symbolic evidence references. Domain owners may refactor internal helpers into one atomic composite action when their consistency boundary requires it; Workflow treats that declared action as one transition rather than splitting its transaction.
