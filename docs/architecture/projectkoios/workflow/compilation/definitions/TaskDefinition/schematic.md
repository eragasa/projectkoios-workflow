# `TaskDefinition` schematic

## Responsibility

```text
TaskDefinition
   ├── identity
   ├── route kind
   ├── request/result schema references
   └── action or nested-target reference
                     │
                     ▼
      transition/action mapping in plan
```

The compiler verifies that every task definition maps completely and exactly into the flat CPN plan.
