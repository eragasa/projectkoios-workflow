# `projectkoios.workflow.sdk.registry` schematic

## Responsibility

```text
external package metadata
+ action and schema descriptors
+ provider/environment capabilities
               │
               ▼
WorkflowPluginManifestProvider
               │ canonical frozen manifest
               ▼
isolated worker/exporter registration
               │ authenticated request
               ▼
persistent Workflow registry
```

The manifest content digest changes whenever any advertised contract, environment, or guarantee changes.
