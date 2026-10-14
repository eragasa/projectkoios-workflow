# `projectkoios.workflow` implementation

> **Status: provisional architecture candidate.** This file compares possible
> implementation boundaries; it is not an implementation sequence or approval.

## Responsibility

The current candidate separates a stable SDK surface from service internals. The SDK would contain frozen records, ABCs, and validating bases; service internals would contain the compiler, kernel, registry, runtime, persistence, scheduler, and transports. Whether these become separate distributions, one distribution with enforced import boundaries, or staged packages is unresolved.

Primary migration evidence is the compiler/plan/binding architecture at `ksdft2effmass` commit `5210b760c6c13f9f5980a649f0a85362a26b5d2d`, adapted to canonical CPN IR. Frankenstein commit `3eb562f2d6167ec20d6f2c892c517509a7abf283` supplies fragment-template, deterministic composition, and visualization design evidence. The current `projectkoios.workflow.petrinet.colored` package supplies kernel conformance evidence with its own recorded provenance. Evidence constrains semantics but does not require copying historical class layouts.

## Alternatives retained

- **Packaging:** separate SDK/service/worker distributions, or one distribution with mechanically enforced dependency layers.
- **Compiler hosting:** isolated definition exporter, administrative compiler worker, or effect-free control-plane operation.
- **Link timing:** deployment activation, run admission, or an explicitly versioned prelinked bundle.
- **Operational lifecycle:** one composed flat operational/domain CPN, or a separately compiled companion CPN correlated to the domain occurrence; either must preserve one authoritative CPN semantics and prevent failed effects from fabricating domain firing.
- **Reservation representation:** keep domain inputs in the predecessor marking plus an engine reservation record until success, or let an explicit `begin_occurrence` transition consume them into a lossless occurrence token. The latter makes operational ownership visible in the marking but decomposes one logical effect into a lifecycle subnet. In both candidates, `commit_occurrence` may realize the reserved logical/domain transition only for admitted success. Failure, rejection, cancellation, loss, or ambiguity cannot masquerade as that firing.
- **Worker dispatch:** worker pull claims or authenticated control-plane push, with identical lease and ambiguity guarantees.
- **Local supervision:** generic durable supervisor or provider-owned launch ledger; bare child-process ownership is insufficient.
- **Persistence:** hardened SQLite for the laptop deployment or another transactional store if concurrency and backup evidence require it.

## Sequencing options, not commitments

1. Harden and accept the pure CPN kernel before compiler work.
2. Transfer the DEFECT00003 compiler/linker invariants first against a stub CPN IR.
3. Build a thin end-to-end conformance skeleton and then deepen kernel, compiler, and provider guarantees in parallel.
4. Use the 1,158-identity Ingestion corpus only after shared cross-family protocol fixtures pass, or use its non-executing fixture plan earlier as a compiler stress case.

Architecture review should select or combine these approaches using risk and evidence. None is authorized by its presence here.

## Common evidence gates

- Immutable plan independence from live owners and providers.
- Exact CPN enablement, selection, reservation, external-output admission, and firing equivalence under both reservation candidates.
- Explicit failure-evidence routing: a domain failure token requires a separate guarded domain transition; provider failure alone never fires the reserved domain transition.
- Crash-before/after-launch, ambiguity, reconciliation, cancellation, and restart tests.
- Same-store replay and independent rebuild without effect re-execution.
- Authority separation and private-data redaction.
- Cross-owner provider conformance and exact registry/link resolution.
- Migration equivalence before any script, façade, or historical engine retires.

The existing core and local runtime remain prototypes. Supersession, reuse, or retirement is an architecture-review decision followed by separately authorized implementation and migration work.

## Issue register

Stable Workflow-local questions and external dependency gates are retained in the [provisional issue register](issues/). Module documents should reference those identities rather than copying mutable status. Cross-repository product decisions and external-owner defects remain authoritative in their owning repositories.
