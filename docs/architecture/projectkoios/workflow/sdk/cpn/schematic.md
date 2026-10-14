# `projectkoios.workflow.sdk.cpn` schematic

## Responsibility

```text
base fragment template
        │ declared inheritance and semantic delta
        ▼
external specialized template
        │ instantiate(namespace, parameters)
        ▼
immutable fragment + public ports
        │ deterministic composition
        ▼
flat CPN definition
```

Fragment boundaries remain provenance and visualization annotations. They do not survive as hierarchical runtime execution boundaries.
