# `projectkoios` namespace implementation

## Responsibility

This level maps the architecture to distribution boundaries.

The current repository imports no runtime dependency providing `projectkoios.base`; resolving that packaging boundary is a prerequisite for implementing the target SDK. The preferred direction is a small stable contracts distribution rather than coupling the Workflow service to an application aggregate.

No scientific package may become a dependency of the CPN kernel, compiler, registry, persistence layer, or control plane. External packages publish canonical descriptors and typed envelopes. Environment-specific code is hosted by workers in pinned isolated environments.

Namespace packages must avoid broad re-exports. Curated public surfaces belong at deliberate SDK, client, or composition roots.
