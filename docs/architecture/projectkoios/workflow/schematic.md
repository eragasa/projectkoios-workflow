# `projectkoios.workflow` schematic

> **Status: provisional architecture candidate.** The pipeline expresses the
> strongest current evidence, but its physical process and package boundaries
> remain open.

## Responsibility

This schematic separates candidate authoring, compilation, deployment linking, pure execution, and operational-effect responsibilities.

```text
external SDK implementations
  AbstractWorkflow / AbstractTask / fragment templates / action bindings
                              │
                              ▼
                  immutable source definitions
                              │
                              ▼
                 compiler + fragment composer
                              │
                              ▼
         WorkflowExecutionPlan with canonical flat CPN IR
                              │
                              ▼
                   deployment binding linker
                              │
                              ▼
                exact worker/provider bindings
                              │
                              ▼
marking → enablement → selection → reservation → provider attempt
   ▲                                                   │
   └──────────── atomic pure firing on admitted success ┘
```

Registry discovery precedes compilation and linking. The engine receives already compiled and linked artifacts and performs no provider discovery.

The reviewed alternatives concern where these phases run, not whether the immutable-plan/runtime-binding separation is preserved: compilation may be an administrative service operation or an isolated exporter job; linking may occur at registration, deployment activation, or run admission; worker dispatch may be pull- or push-oriented. Each option must still keep discovery outside pure CPN firing and live implementations outside plan artifacts.
