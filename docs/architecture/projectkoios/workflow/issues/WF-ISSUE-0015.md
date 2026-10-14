# WF-ISSUE-0015 — Submission boundary between Workflow and provider SPI

- **Kind:** architecture
- **Status:** OPEN
- **Workflow-local scope:** occurrence admission, provider request, and start lifecycle
- **Authoritative owner:** Workflow architecture with provider-owner compatibility evidence

## Problem or question

Is simulation submission an explicitly authored Workflow CPN port/transition that creates a provider request token, or is submission itself a provider SPI operation alongside prepare/stage/start?

## Current evidence

The Simulations refactor proposes `SimulationRequest`, `SimulationRequestor`, immediate `SimulationResponse`, and later `SimulationResult`. Its current recommendation is that request submission be a Workflow port while the provider crosses the external boundary only after claim, preparation, lease, and grant. Existing `SubmitPwDftScfTask` combines application lifecycle meaning with provider dispatch and cannot define the generic boundary.

## Consequence

An unclear boundary can duplicate queue state, treat acceptance as execution, or allow provider-local task stores to become a second scheduler. It also affects when occurrence identity, attempt identity, authority, and idempotency keys become mandatory.

## Alternatives and recommendation

Alternative A makes submission a pure Workflow transition producing a typed provider-request token; provider lifecycle begins later with prepare/stage/start. Alternative B includes an immediate provider `submit/accept` SPI operation before start. The current recommendation is A unless an owner demonstrates that remote admission itself is an external effect requiring its own lifecycle evidence. In either case, acceptance is neither start nor completion.

## Resolution gate

Traces distinguish request construction, queue/worker claim, provider acceptance/rejection, pre-effect preparation, dispatch intent, start acknowledgement, ambiguity, and terminal result. No provider-owned queue becomes authoritative Workflow state, and current Applications/Simulations compatibility paths have an explicit mapping.

## Affected architecture

CPN action ports, lifecycle SPI, compiler lowering, occurrence creation, provider request/response records, and `WF-ISSUE-0014`.
