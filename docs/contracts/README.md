# Workflow contracts

This directory contains stable contract proposals and accepted contracts owned
by `projectkoios-workflow`.

| Contract ID | Authoritative document | Scope |
|---|---|---|
| `projectkoios.workflow.core` | [`workflow-core.md`](workflow-core.md) | Proposed Petri-independent workflow core |
| `projectkoios.workflow.runtime` | [`workflow-runtime.md`](workflow-runtime.md) | Candidate bounded append-only local runtime Slice A |
| `projectkoios/workflow/v0.1` | [`workflow-cpn-bindings.md`](workflow-cpn-bindings.md) | Candidate Generic Workflow CPN execution, plan, child, and deployment contract |
| `projectkoios/workflow/v0.1` imports | [`workflow-cpn-public-imports.md`](workflow-cpn-public-imports.md) | Proposed semantic-owner inventory only; no implementation binding or consumer gate |

Cross-repository discovery is provided by the
[Project Koios contract catalog](https://github.com/eragasa/projectkoios/blob/main/docs/contracts/README.md).
Lifecycle, pre-release versioning, compatibility, and conformance follow the
[Project Koios contract governance policy](https://github.com/eragasa/projectkoios/blob/main/docs/policies/contracts.md).
Task and recovery authority rules are defined by the
[Project Koios task and recovery policy](https://github.com/eragasa/projectkoios/blob/main/docs/policies/task-and-recovery-records.md).

The contract document itself is authoritative for status and version. This
index does not authorize implementation, production transfer, consumer
migration, release, deprecation, or source removal.
