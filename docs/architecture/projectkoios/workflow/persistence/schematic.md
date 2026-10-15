# `projectkoios.workflow.persistence` schematic

## Responsibility

```mermaid
flowchart TD
    Private[Shared private SQLite path and connection policy]
    Revision[Opaque revision adapter] --> Private
    Pure[Pure-action reservation adapter] --> Private
    Private --> Schema[Adapter-owned exact schema validation]

    Command[Pure-action commit candidate] --> Revalidate[Revalidate source observations]
    Revalidate --> Encode[Encode canonical identity-only commit event]
    Encode --> Rows[Pure-action row codecs and digest validation]
    Rows --> Tx[SQLite BEGIN IMMEDIATE]
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

Both SQLite adapters share private-file and connection security policy while
retaining separate schemas and transaction orchestration. The experimental
pure-action repository and replay service cover durable reservation, compact
atomic commit, and structural identity-chain replay only. Complete durable CPN
and runtime safety-state replay remains separate work.
