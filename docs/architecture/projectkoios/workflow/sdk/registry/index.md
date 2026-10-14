# `projectkoios.workflow.sdk.registry` architecture

## Responsibility

The SDK registry module defines immutable plugin, action, provider, schema, environment, and capability descriptors plus the ABC used by external packages to publish one canonical manifest. It is a declaration boundary, not the persistent service registry.

A manifest states exactly what an installed package can implement. It does not select that package for a run and does not constitute authority to execute an effect.
