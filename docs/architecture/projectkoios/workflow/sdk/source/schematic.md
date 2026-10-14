# `projectkoios.workflow.sdk.source` schematic

## Responsibility

```text
external AbstractWorkflow subclass
       ├── identity
       ├── immutable fragment composition
       └── ordered AbstractTask owners
                    │
                    ▼ final base properties
       WorkflowSourceDefinition
       TaskSourceDefinition tuple
                    │
                    ▼
             CPN plan compiler
```

The source objects are temporary compiler inputs. Their frozen definitions cross the compilation boundary; live owners do not.
