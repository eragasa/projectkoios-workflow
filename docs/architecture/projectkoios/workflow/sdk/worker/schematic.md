# `projectkoios.workflow.sdk.worker` schematic

## Responsibility

```text
WorkflowWorkerPlugin
├── WorkflowPluginManifestProvider
├── TransitionActionBinding implementations
└── ExternalLifecycleProvider implementations
             │ loaded in isolated environment
             ▼
       generic worker host
             │ exact claim/occurrence requests
             ▼
       typed results/evidence
```

The plugin never receives a mutable marking or database connection.
