# `WorkflowWorkerPlugin` schematic

## Responsibility

```text
entry point
   │ instantiate
   ▼
WorkflowWorkerPlugin
   ├── manifest_provider()
   ├── action_bindings()
   └── lifecycle_providers()
             │ host validation
             ▼
       active worker capability
```

Manifest and implementations must form one exact closed set before the worker reports readiness.
