# `projectkoios.workflow.sdk.cpn` architecture

## Responsibility

The SDK CPN module owns reusable fragment-template authoring contracts. External scientific or operational packages subclass declared templates, instantiate them with an immutable namespace and parameters, and return closed fragments containing colors, places, transitions, arcs, guards, inscriptions, and typed ports.

Template inheritance is restricted to declared extension points. Kernel definition and marking records are immutable values and are never subclassed.
