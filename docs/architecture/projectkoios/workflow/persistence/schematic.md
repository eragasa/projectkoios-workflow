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
    Commit --> Lifecycle[Append commit-bound reservation lifecycle event]
    Lifecycle --> References[Insert ordered evidence references]
    References --> Bundle[Retain content-addressed CPN replay bundle and link]
    Bundle --> Consume[Consume reservation]
    Consume --> Advance[Advance marking coordinate]
    Advance --> Durable[SQLite COMMIT with synchronous FULL]

    Durable --> Reopen[Reopen database]
    Reopen --> Inspect[Verify event bytes, typed fields, and coordinates]
    Inspect --> Replay[Read-only compact commit reconstruction]
    Inspect --> History[Reconstruct identity-only reservation lifecycle]
    Inspect --> Safety[Correlate bounded committed safety-state snapshot]
    Inspect --> Correlate[Correlate commit and replay evidence]
    Correlate --> Refire[Pure CPN refiring]

    Command -. no owner payload bodies .-> Outside[Owner-controlled storage]
    Replay -. no owner or CPN invocation .-> Done[Replayed compact evidence]
    History -. no owner, source, or CPN invocation .-> Done
    Safety -. decode markings without firing .-> Done
    Refire -. no owner or source invocation .-> CpnDone[Replayed CPN result]
```

Both SQLite adapters share private-file and connection security policy while
retaining separate schemas and transaction orchestration. The experimental
pure-action repository and replay services cover durable reservation, compact
atomic commit, structural identity-chain replay, and bounded pure-CPN transcript
refiring. Complete request/result history, reservation lifecycle, and runtime
safety-state replay remain separate work.
