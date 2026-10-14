# `WorkflowPluginManifestProvider`

## Responsibility

`WorkflowPluginManifestProvider` is the nominal external source of one immutable package manifest. It exposes exact definition-provider, action-binding, lifecycle-provider, worker, schema, and capability descriptors for an installed distribution/environment.

It performs no registration itself and returns no live provider objects.
