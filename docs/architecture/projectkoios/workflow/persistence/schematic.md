# `projectkoios.workflow.persistence` schematic

## Responsibility

```text
service command
      │ one transaction
      ├── append immutable event(s)
      ├── update marking/runtime projections
      └── append dispatch outbox intent
                 │
                 ▼
worker gateway delivery and acknowledgement

replay: events + immutable artifacts → rebuilt projections
```

Outbox intent is durable before an external launch is requested.
