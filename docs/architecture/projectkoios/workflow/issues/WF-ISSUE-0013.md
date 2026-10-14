# WF-ISSUE-0013 — Architecture correctness and acceptance evidence

- **Kind:** evidence
- **Status:** OPEN
- **Workflow-local scope:** provisional architecture review
- **Authoritative owner:** Workflow architecture review; product-wide decisions remain in `projectkoios`

## Problem or question

What evidence is sufficient to accept, revise, or reject the current package/class decomposition and proceed to separately authorized implementation planning?

## Current evidence

The repository test verifies that every architecture directory has substantive `index.md`, `schematic.md`, and `implementation.md` documents. It does not verify semantic correctness. The current draft synthesizes Workflow, Frankenstein, `ksdft2effmass`, Applications, Ingestion, References, Simulations, and Laptop evidence but has not received an accepted architecture decision.

All interactive Project Koios Pi sessions represent the same human operator. Cross-session reviews may supply independently reasoned technical evidence, but they are not independent-human approval and cannot authorize acceptance, implementation, migration, or another protected operation. The eventual operator decision must remain a separate explicit record.

## Consequence

Treating documentation structure or reviewer inventory as architecture acceptance could prematurely lock package names, service boundaries, or migration sequence.

## Alternatives and recommendation

Use bounded independently reasoned technical review against representative CPN traces and owner contracts. Do not describe another Pi session as a second human approver. Record disagreements and alternatives here; resolve product-wide choices in `projectkoios`; accept public semantics only through contract governance and a separate explicit operator decision.

## Resolution gate

A durable review record addresses compiler/linker mutation safety, CPN semantics, external lifecycle faults, security/privacy, replay/provenance, deployment recovery, cross-owner compatibility, and the first serious corpus definition. It explicitly states accepted decisions and deferred alternatives.

## Affected architecture

The entire provisional tree and any later implementation authorization.
