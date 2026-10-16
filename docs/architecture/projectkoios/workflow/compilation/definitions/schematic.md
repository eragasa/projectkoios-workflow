# `projectkoios.workflow.compilation.definitions` schematic

## Responsibility

```mermaid
classDiagram
    class TaskDefinition {
      +task identity
      +definition kind
      +contract version
    }
    class AtomicTaskDefinition {
      +pure or effectful route descriptor
    }
    class WorkflowDefinition {
      +ordered Task instances
      +composition
      +input/export contracts
    }
    TaskDefinition <|-- AtomicTaskDefinition
    TaskDefinition <|-- WorkflowDefinition

    class WorkflowExecutionPlanConstructor
    TaskDefinition --> WorkflowExecutionPlanConstructor
```

Definition equality is structural and content-bound. A source-owner change
creates another definition identity rather than mutating retained state.
