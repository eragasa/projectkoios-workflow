# `projectkoios.workflow.persistence` schematic

## Responsibility

```mermaid
flowchart TD
    Command[Pure-action commit candidate] --> Revalidate[Revalidate source observations]
    Revalidate --> Encode[Encode canonical identity-only commit event]
    Encode --> Tx[SQLite BEGIN IMMEDIATE]
    Tx --> Check[Verify active reservation and current predecessor]
    Check --> Commit[Insert compact fields and exact event bytes]
    Commit --> References[Insert ordered evidence references]
    References --> Consume[Consume reservation]
    Consume --> Advance[Advance marking coordinate]
    Advance --> Durable[SQLite COMMIT with synchronous FULL]

    Durable --> Reopen[Reopen database]
    Reopen --> Inspect[Verify event bytes, typed fields, and coordinates]
    Inspect --> Replay[Read-only compact commit reconstruction]

    Command -. no owner payload bodies .-> Outside[Owner-controlled storage]
    Replay -. no owner or CPN invocation .-> Done[Replayed compact evidence]
```

The experimental repository and replay service cover durable reservation,
compact atomic commit, and structural identity-chain replay only. Complete CPN
and runtime safety-state replay remains separate work.
