# `projectkoios.workflow.compilation.bindings` architecture

## Responsibility

The bindings module links one exact compiled Workflow plan to one complete
route-compatible deployment. It verifies pure firers, effect lifecycle handlers,
worker environments, and separately deployed child Workflow plans without
modifying plan semantics.

Atomic Tasks link to exact owner execution descriptors. Workflow-backed Tasks
link to exact child-plan deployments and child-run services. Binding is distinct
from discovery and invocation; runtime receives a complete artifact and never
silently chooses another provider or child definition.
