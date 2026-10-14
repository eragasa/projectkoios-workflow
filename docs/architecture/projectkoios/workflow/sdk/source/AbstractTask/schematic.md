# `AbstractTask` schematic

## Responsibility

```text
AbstractTask subclass
   ├── pure typed action route
   ├── external lifecycle route
   └── nested-net route
             │ final definition property
             ▼
       TaskSourceDefinition
             │ compile-time mapping
             ▼
 CPN transition/action binding
```

Only one route is admitted. Route choice controls linking and invocation behavior but never replaces CPN enablement or firing semantics.
