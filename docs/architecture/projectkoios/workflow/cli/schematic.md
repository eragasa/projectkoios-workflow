# `projectkoios.workflow.cli` schematic

## Responsibility

```text
operator arguments
      │ strict local parsing
      ▼
CLI request constructor
      │ authenticated client
      ▼
Workflow API/service actionizer
      │
      ▼
structured result → stable human/JSON rendering
```

Dry-run operations validate and resolve without performing protected domain effects. A CLI success code is not scientific or publication approval.
