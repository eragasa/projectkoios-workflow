# `projectkoios.workflow.sdk.cpn` implementation

## Responsibility

Implement the fragment records and bases from the reviewed Frankenstein `docs/architecture/cpn-composition/**` design at commit `3eb562f2d6167ec20d6f2c892c517509a7abf283`. This is design-based adaptation: Frankenstein contains no generic CPN implementation under its `cpn` source package.

Validation must reject undeclared base mutation, weakened ports, unresolved internal references, and unstable identity generation. Composition behavior belongs to the service-side CPN composer rather than the external template.
