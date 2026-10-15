# `projectkoios.workflow.persistence` schematic

## Responsibility

```mermaid
flowchart TD
    Command[Pure-action commit candidate] --> Revalidate[Revalidate source observations]
    Revalidate --> Tx[SQLite BEGIN IMMEDIATE]
    Tx --> Check[Verify active reservation and current predecessor]
    Check --> Commit[Insert compact commit fields]
    Commit --> References[Insert ordered evidence references]
    References --> Consume[Consume reservation]
    Consume --> Advance[Advance marking coordinate]
    Advance --> Durable[SQLite COMMIT with synchronous FULL]

    Durable --> Reopen[Reopen database]
    Reopen --> Inspect[Reconstruct commit record and current coordinate]

    Command -. no owner payload bodies .-> Outside[Owner-controlled storage]
```

The experimental repository covers durable reservation and compact atomic
commit only. Canonical committed-event replay and complete workflow history
remain separate work.
