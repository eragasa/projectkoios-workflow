# Workflow architecture issue register implementation

> **Status: provisional governance candidate.** No issue here authorizes source
> implementation, migration, external execution, or release.

## Responsibility

Each `WF-ISSUE-NNNN.md` record contains: stable ID, immutable kind, current status, Workflow-local scope, authoritative owner, problem or question, exact evidence, consequence, alternatives, current recommendation, resolution gate, and affected architecture paths.

Candidate statuses are `OPEN`, `NARROWED`, `BLOCKED_BY_DEPENDENCY`, `DEFERRED`, and `RESOLVED`. Status is descriptive, not an action authorization. Accepted Workflow decisions should be retained in durable decision records; accepted public semantics move into `docs/contracts/` only after separate review. Product-wide decisions remain authoritative in `projectkoios`.

Records exclude assignees, session identities, ETAs, transient progress, and replicated work queues. External-owner gaps use dependency language and must link to durable owner evidence before resolution. Module documents may reference issue IDs but should not copy mutable status prose.
