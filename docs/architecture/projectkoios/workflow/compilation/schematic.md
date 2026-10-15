# `projectkoios.workflow.compilation` schematic

## Responsibility

```mermaid
flowchart TD
    Registry[registry-resolved source owners] -->|final frozen definitions| Definitions[definitions]
    Definitions --> Compiler[planning/compiler]
    Compiler --> Plan[WorkflowExecutionPlan]
    Descriptors[provider/environment descriptors] --> Linker[binding linker]
    Plan --> Linker
    Linker --> Bindings[WorkflowExecutionBindings]
    Bindings --> Runtime[runtime CPN engine]

    DefinitionBytes[canonical flat-definition bytes] --> DefinitionDecoder[strict definition decoder]
    DefinitionDecoder --> Definition[CPN definition]
    MarkingBytes[canonical semantic-marking bytes] --> MarkingDecoder[strict marking decoder]
    MarkingDecoder --> Marking[CPN marking]
    DefinitionDecoder --> Reencode[exact byte re-encoding required]
    MarkingDecoder --> Reencode
```

Discovery occurs before compilation and linking. Runtime receives exact artifacts
and performs no identity-only inference. Representation decoding reconstructs
candidate semantic objects but does not itself grant runtime authority.
