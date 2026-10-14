# `projectkoios` namespace schematic

## Responsibility

This schematic shows dependency direction at the shared namespace boundary.

```text
projectkoios base contracts
        │
        ├── projectkoios.workflow SDK and service
        │          ▲
        │          │ SDK implementations and canonical manifests
        ├── ingestion providers
        ├── reference providers
        ├── simulation providers
        └── application/scientific definition providers

compiled Workflow definitions and runs
        ▲
        ├── ksdft2effmass composition
        └── Applications composition → API/Web → Laptop bundle
```

External owners depend on the stable Workflow SDK. The Workflow kernel and control-plane service never import those owners. Higher product layers consume clients and compiled definitions rather than reaching laterally into worker internals.
