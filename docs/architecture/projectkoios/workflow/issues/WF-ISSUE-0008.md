# WF-ISSUE-0008 — Ingestion provider-action readiness

- **Kind:** dependency
- **Status:** BLOCKED_BY_DEPENDENCY
- **Workflow-local scope:** complete typed action coverage for Ingestion-bound transitions
- **Authoritative owner:** `projectkoios-ingestion`

## Problem or question

Which remaining Ingestion operations need stable workflow-facing request/actionizer/result contracts before their script orchestration can be represented solely by compiled CPN transitions?

## Current evidence

Accepted lower-layer revisions include `6f5a56d` for A-artifact validation, selected Mongo recovery, and projection inventory; `618ded0` for disk-only journal publication; and `9de69bc` for bounded Class-C extraction/freeze. Ingestion master `1274519` (PR #59) introduced an Ingestion-local pure Projector framework under `ingestion/base/projector/`: a typed stateless source/config/value and canonical request/result boundary with stable identity and explicit rejection of effects, authority, retry, materialization, workflow state, and arbitrary contracts. Master `5d4b450` (PR #60) adds its first concrete pure extraction projector, producing an immutable backend-neutral `ExtractionReadModel` from exact publication evidence and configuration with fixed `Contract`, `Payload`, and `Identity` error categories. Mongo materialization remains a separate effectful owner operation, with the owner composition `read → project → index-readiness → materialize`. These are owner-internal pure transformation primitives—not Workflow provider or lifecycle bases—and PR #60 adds no Workflow coupling or operational recovery. Full-content inventory, explicit target identity, frozen nested invariants, and operational migration remain open owner dependencies. A concrete Workflow-facing Ingestion action may use the projector internally and expose its result through the Workflow SDK transition-action boundary. No corpus or Mongo execution occurred. The wider numbered 001–034 inventory still contains partial or missing collection-level plan, validation, composition, audit, and publication actions.

The current Workflow runtime explicitly provides no claim, lease, external dispatch, or migration facility. Consequently a development-only owner migration cannot truthfully require a “Workflow-owned lease” today. This absence is not itself a hard blocker to a separately authorized one-time migration if an operator/deployment-controlled exclusive maintenance window mechanically excludes or observes every other writer. That manual mechanism does not transfer future migration-orchestration ownership to Ingestion and cannot claim Workflow lease or runtime conformance.

Minimum freeze evidence binds the exact migration-plan digest, development target/store, authorization decision, designated sole writer, bounded window or release condition, freeze mechanism, complete known-writer inventory and quiescence evidence, and pre-migration head/generation/inventory. Closure evidence binds the acquire record, migration outcome, post-migration head/generation/inventory and drift checks, and release/restore observation. A bare assertion, PID, development label, or equal counts is insufficient; inability to exclude or observe another writer remains a hard stop.

## Consequence

The priority 1,158-identity corpus CPN can be compiled only against the accepted subset or test doubles; full Ingestion script retirement is blocked.

## Alternatives and recommendation

Workflow should record required action descriptors and evidence gates without duplicating Ingestion defects or implementing domain behavior. Prioritize the exact corpus inventory/join, same-store verification, and independent-rebuild comparison contracts, then address other numbered workflows by migration dependency.

## Resolution gate

Durable owner records and accepted clean revisions provide every referenced contract, including full-content inventory, explicit target identity, frozen nested invariants, and operational migration; registry/linker conformance resolves exact versions; retained fixtures prove identity and failure equivalence. The provisional corpus CPN keeps pure projection distinct from effectful Mongo materialization and preserves owner atomicity and error semantics. Any interim development migration records the operator/deployment freeze as an explicit bounded exception and future Workflow replacement point rather than satisfying the unresolved production lease/runtime gate.

## Affected architecture

Definition providers, action registry, corpus fragments, migration equivalence, and owner dependency reporting.
