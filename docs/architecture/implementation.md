# Architecture documentation implementation

> **Status: provisional architecture candidate.** No implementation or
> migration is authorized by this document.

## Responsibility

This document defines how architecture documentation is maintained while alternatives are reviewed and, only after a separate decision, as code evolves.

The initial tree describes candidate architecture before implementation. Each `implementation.md` distinguishes proposed responsibility, current evidence, unresolved design, and required gates. Concrete package and class paths are working names. A future implementation may use different names or boundaries if a reviewed decision records the alternative and preserves the required semantics.

A repository test verifies that every directory contains `index.md`, `schematic.md`, and `implementation.md`, that each file states a responsibility, and that no file is an empty link collection. It does not validate the architectural choices. Source migrations would additionally require provenance manifests with commit, tree, path, blob identity, adaptation notes, conformance tests, and rollback treatment.

## Evidence gates before implementation planning

- Review the compiler/source-IR/CPN-IR/linker split against DEFECT00003.
- Compare single-distribution and split-SDK/service/worker packaging.
- Resolve authority issuer, process-supervisor, cancellation, and terminal-success boundaries.
- Validate the provider protocol against Ingestion, References, Simulations, Applications, and `ksdft2effmass` fixtures.
- Decide persistence and deployment only after crash, replay, reconciliation, privacy, and backup requirements are explicit.
- Record accepted provenance and exclusions for Frankenstein and `ksdft2effmass` source evidence.

The architecture tree must not silently make a proposal into an accepted public contract. Contract status remains under `docs/contracts/` until explicitly changed, and implementation requires separate authorization.
