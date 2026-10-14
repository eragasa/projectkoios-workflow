# `projectkoios.workflow.worker` schematic

## Responsibility

```text
control plane outbox/claim
          │ authenticated occurrence request
          ▼
isolated worker host
  ├── plugin manifest
  ├── transition action binding
  ├── lifecycle provider
  └── durable provider launch ledger
          │ typed result/evidence
          ▼
control plane ingress and engine admission
```

Each worker has a strong process identity, capability scope, availability state, and drain lifecycle.
