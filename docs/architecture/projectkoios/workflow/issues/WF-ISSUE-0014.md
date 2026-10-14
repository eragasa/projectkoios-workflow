# WF-ISSUE-0014 — Simulations action and lifecycle boundary readiness

- **Kind:** dependency
- **Status:** BLOCKED_BY_DEPENDENCY
- **Workflow-local scope:** simulation action descriptors and external-lifecycle bindings
- **Authoritative owner:** `projectkoios-simulations`

## Problem or question

Which current simulation contracts remain runtime-neutral action colors and transformations, and which task/lifecycle wrappers must be replaced by standardized Workflow occurrence fragments before concrete DFT definitions can link cleanly?

## Current evidence

Read-only inventory at `f3e7ee568434313b0c36e7e304484a4fac6e0a63` identifies neutral scientific contracts such as `PwDftScfRequest`, observations, results, native evidence, render/projection/parser/normalization ports, and provider-specific saved-state semantics. These are valid seeds for typed action descriptors. Current `RegisterPwDftScfTask`, `SubmitPwDftScfTask`, submitted/completed task events, handler task stores, and workflow start/outcome wrappers encode operational lifecycle. `AnalyzePwDftScfOutput` is tied to task identity rather than a runtime-neutral evidence-to-normalized-result contract.

The Simulations owner synthesis classifies pure render/project/parse/normalize actions, external calculator lifecycle providers, explicit operational evidence colors, and SCF/NSCF/relaxation/pw2wannier90/EPW/VASP migration mappings. That synthesis is canonical evidence for Simulations-owned classification only. Its begin/consume lowering is one candidate mapping under [`WF-ISSUE-0012`](WF-ISSUE-0012.md), not a platform decision. Its wording that one commit may emit scientific failure tokens is superseded at the Workflow boundary: unsuccessful attempts emit operational evidence, and a separate explicitly declared guarded domain transition is required for any scientific/domain failure token.

The authorized representative refactor is isolated at `/Users/eugene/repos/projectkoios-simulations-qe-scf-actions`, branch `owner-refactor/qe-scf-runtime-neutral-actions`, based on `f3e7ee568434313b0c36e7e304484a4fac6e0a63`. Its scope is QE SCF runtime-neutral BaseObject contracts, reusable simulation/projection bases, a common QE/PW/SCF hierarchy, documentation, tests, and compatibility. Calculator execution, network/private state, Workflow SDK dependency, commit, and push were excluded.

The owner has now implemented and locally validated the documented neutral/provider split in the isolated uncommitted worktree. `simulations/base/simulation.py` supplies immutable scientific `Simulation`; `DftPwSimulation` is primary with `PwDftSimulation` compatibility alias; `DftPwScfSimulation` is the SCF leaf. `integrations/base` supplies repository-local nominal artifact contracts, resources, and asynchronous `SimulationRequest`, `SimulationRequestor`, `SimulationResponse`, and `SimulationResult` boundaries without importing a Workflow SDK.

The QE hierarchy now uses immutable `QeSimulation`, `QePwSimulation(QeSimulation, DftPwSimulation)`, and `QePwScfSimulation(QePwSimulation, DftPwScfSimulation)`. `QePwSimulation` owns a `QePwInputFile`, pseudopotentials, and multiple typed output declarations; the input file owns its filename. The request carries complete staged references/resources, the abstract requestor returns immediate accept/reject response, and the later correlated result carries multiple output artifacts. Historical singular filename keywords are compatibility adapters into canonical nested state rather than duplicated storage.

The current clean local evidence is 433 tests passed, 4 skipped, and 204 subtests; Ruff check and format passed; strict mypy passed for 45 neutral files and all 179 simulation/integration files; a wheel built with both base namespaces and the QE hierarchy; and `git diff --check` passed. The primary checkout remains clean. No calculator, network, commit, or push occurred. This evidence validates an owner-local uncommitted slice, not an accepted cross-repository SPI or Workflow contract.

Pure QE SCF operations remain request projection, deterministic input rendering, exact-output parsing, and normalization as four separate actions. Existing blocking executor/handler, combined projector/extractor, task actions/events/stores, wrappers, and `QuantumEspressoSimulation`/`PwDftSimulation` aliases remain compatibility seams; none has been deleted. Queue storage, resource leases, scoped grants, dispatch, observe/reconcile/cancel/collect action families, and durable idempotency remain intentionally unimplemented pending Workflow architecture.

## Consequence

Without a reviewed split, the compiler could accidentally preserve provider-local task state or duplicate Workflow occurrence semantics, while discarding useful neutral scientific contracts.

## Alternatives and recommendation

Retain immutable neutral colors/ports and pure typed request-to-result/evidence transformations in Simulations. Refactor output analysis into an evidence-to-normalized-result action. Replace registration, submission, task-store, and task-event lifecycle with standardized Workflow occurrence/lifecycle fragments. Workflow source definitions explicitly bind action and provider identities; neither compiler nor adapter infers arcs, loops, retry, concurrency, or scientific acceptance.

Authoritative Workflow replay rehydrates retained definitions, plans, markings, occurrences, results, and evidence without invoking even pure owner actions. Optional re-execution of a pure Simulations action is separate verification/rebuild with pinned implementation and inputs; it creates new comparison evidence and never repairs or mutates original history.

## Resolution gate

A clean accepted owner revision must preserve the now-validated immutable simulation hierarchy, asynchronous request/response/result, artifact, resource, and compatibility contracts and publish stable descriptors for pure render/project/parse/normalize actions. Current lifecycle wrappers need an explicit compatibility/retirement plan. The still-unimplemented lease/grant/dispatch/observe/reconcile/cancel/collect and idempotency behavior must bind to reviewed Workflow contracts rather than being inferred from owner-local envelopes. SCF, NSCF, relaxation, pw2wannier90, EPW, and VASP fixtures must pass registry/linker and occurrence-protocol conformance without domain imports in the service.

Before a cross-repository SPI freezes, Workflow architecture must resolve or explicitly defer: canonical occurrence/attempt context fields; whether submission is a Workflow port or provider SPI operation; exact lease/grant/cancel/reconcile/result-delivery colors; the durable artifact resolver boundary and `operation_id` owner; and idempotency scope across occurrence and attempt. Owner refactoring does not need to wait for or import provisional Workflow types.

## Affected architecture

SDK actions and lifecycle, compiler action mapping, provider registry/linker, external occurrence alternatives in [`WF-ISSUE-0012`](WF-ISSUE-0012.md), submission ownership in [`WF-ISSUE-0015`](WF-ISSUE-0015.md), artifact/operation identity in [`WF-ISSUE-0016`](WF-ISSUE-0016.md), idempotency scope in [`WF-ISSUE-0017`](WF-ISSUE-0017.md), DFT definition migration, and success-layer contracts in [`WF-ISSUE-0004`](WF-ISSUE-0004.md).
