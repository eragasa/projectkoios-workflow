# Workflow architecture issue register

> **Status: provisional governance candidate.** This register is uncommitted
> review material and is not an adopted work queue or decision system.

## Responsibility

This directory retains stable, linkable records for unresolved questions and evidence gaps owned by or directly blocking `projectkoios-workflow`. It prevents changing alternatives and evidence from being copied into many module documents while keeping uncertainty visible beside the architecture it affects.

The register is not authoritative for cross-repository product architecture or defects owned by another repository. Such records identify the external authority, exact observed revision, dependency expectation, and resolution evidence required by Workflow. They do not duplicate, reclassify, assign, or schedule the owner's work.

Issue identities never encode mutable status. Records remain at the same path after resolution and link to the authoritative decision, contract, owner record, or evidence that closed them.

## Current scope

The initial records cover packaging, authority, process supervision, success layering, cancellation, compatibility, persistence, owner action readiness, missing execution evidence, lifecycle reservation semantics, and architecture-review evidence. Their presence documents uncertainty; it does not select an implementation sequence.

## Records

| Stable ID | Kind | Question or dependency |
|---|---|---|
| [`WF-ISSUE-0001`](WF-ISSUE-0001.md) | architecture | Stable base-contract packaging |
| [`WF-ISSUE-0002`](WF-ISSUE-0002.md) | architecture | Grant issuer and revocation model |
| [`WF-ISSUE-0003`](WF-ISSUE-0003.md) | architecture | Durable local process-supervisor ownership |
| [`WF-ISSUE-0004`](WF-ISSUE-0004.md) | contract | Exact success-layer contracts |
| [`WF-ISSUE-0005`](WF-ISSUE-0005.md) | architecture | Cancellation propagation policy |
| [`WF-ISSUE-0006`](WF-ISSUE-0006.md) | contract | SDK and wire compatibility policy |
| [`WF-ISSUE-0007`](WF-ISSUE-0007.md) | architecture | Event-store, backup, and schema evolution |
| [`WF-ISSUE-0008`](WF-ISSUE-0008.md) | dependency | Ingestion provider-action readiness |
| [`WF-ISSUE-0009`](WF-ISSUE-0009.md) | dependency | References provider-action readiness |
| [`WF-ISSUE-0010`](WF-ISSUE-0010.md) | evidence | EPW real-execution conformance evidence |
| [`WF-ISSUE-0011`](WF-ISSUE-0011.md) | dependency | Silicon workflow owner readiness |
| [`WF-ISSUE-0012`](WF-ISSUE-0012.md) | architecture | External-occurrence reservation representation |
| [`WF-ISSUE-0013`](WF-ISSUE-0013.md) | evidence | Architecture correctness and acceptance evidence |
| [`WF-ISSUE-0014`](WF-ISSUE-0014.md) | dependency | Simulations action and lifecycle boundary readiness |
| [`WF-ISSUE-0015`](WF-ISSUE-0015.md) | architecture | Submission boundary between Workflow and provider SPI |
| [`WF-ISSUE-0016`](WF-ISSUE-0016.md) | architecture | Artifact resolution and operation-identity ownership |
| [`WF-ISSUE-0017`](WF-ISSUE-0017.md) | contract | Idempotency scope across occurrence and attempt |
| [`WF-ISSUE-0018`](WF-ISSUE-0018.md) | dependency | Provisional ksdft2effmass workflow-v2 migration debt |
