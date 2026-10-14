# `projectkoios.workflow.service` schematic

## Responsibility

```text
client/API request
       │ authenticate and authorize control action
       ▼
service actionizer
       ├── registry/compiler/linker
       ├── runtime/CPN engine
       ├── persistence/outbox
       └── worker gateway
       │
       ▼
typed result + event/provenance subscription
```

API authentication and protected-effect authorization are separate checks and records.
