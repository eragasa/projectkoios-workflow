# Workflow architecture issue register schematic

> **Status: provisional governance candidate.**

## Responsibility

```text
module implementation.md
        │ stable issue ID only
        ▼
WF-ISSUE-NNNN.md
├── immutable kind and Workflow-local scope
├── mutable status
├── authoritative owner
├── exact evidence revisions
├── consequences and alternatives
├── current recommendation
└── resolution gate
        │
        ├── Workflow-local decision → durable ADR/contract/commit
        ├── product decision → authoritative projectkoios record
        └── external dependency → owner-repository record/evidence
```

Resolution updates the record in place and adds authoritative evidence. It never renames the issue, deletes its uncertainty history, or rewrites the architecture as though alternatives never existed.
