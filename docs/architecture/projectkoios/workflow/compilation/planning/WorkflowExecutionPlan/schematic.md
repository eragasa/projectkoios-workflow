# `WorkflowExecutionPlan` schematic

## Responsibility

```text
WorkflowExecutionPlan
├── source definition closure
├── flat ColoredPetriNetDefinition
├── initial-marking contract
├── transition/action mapping
├── exact nested targets
├── fragment/composition evidence
└── plan identity and compiler version

(no live runtime objects)
```

The plan is sufficient for structural validation and replay interpretation but not sufficient to dispatch work until linked to an exact deployment.
