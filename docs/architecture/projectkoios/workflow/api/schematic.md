# `projectkoios.workflow.api` schematic

## Responsibility

```text
CLI / Applications client / local UI adapter
                 │ authenticated loopback or Unix socket
                 ▼
             API adapter
                 │ strict typed envelope
                 ▼
          service actionizer
                 │
                 ▼
 typed response or event subscription
```

The API never turns an authenticated client into an effect-authority grant.
