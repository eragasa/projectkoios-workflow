# `projectkoios.workflow.sdk.source` schematic

## Responsibility

```mermaid
classDiagram
    class AbstractTask {
      <<nominal ABC>>
      +identity
      +definition
    }
    class AtomicTask {
      +pure or effectful route
    }
    class AbstractWorkflow {
      +ordered Task instances
      +composition
      +child export contract
    }
    AbstractTask <|-- AtomicTask
    AbstractTask <|-- AbstractWorkflow

    class TaskDefinition
    class WorkflowDefinition
    AbstractTask --> TaskDefinition : final construction
    AbstractWorkflow --> WorkflowDefinition : final construction
    WorkflowDefinition --|> TaskDefinition
```

A parent source composition stores Tasks only. A Workflow source is therefore a
Task source to its parent, but its definition retains composition rather than an
atomic execution route. Live owners end at immutable definition construction.
