# Colored Petri Net shadow-conformance pilot

## Status

Implemented as a non-authoritative shadow under `WORKFLOW-CPN-SHADOW-01`.

This pilot does not transfer production authority, publish a compatibility promise, select a wire format, migrate a consumer, or authorize workflow or scientific execution.

## Source boundary

The production modules under `projectkoios.workflow.petrinet.colored` are byte-identical copies of `ksdft2effmass.petrinet.colored` at clean source revision `be70e856911456402ea2b2562cd2508d0963e4d9` on the observed `dev` branch. The corresponding software-verification tests were copied with a deterministic import-namespace substitution. The public dependency-boundary test was additionally adapted from `ksdft2effmass` domain owners to Project Koios core, runtime, adapter, application, and research-domain owners.

The machine-readable source paths, destination paths, SHA-256 identities, transformation descriptions, source revision, license, Python target, and compatibility limits are recorded in [`provenance/colored-petri-net-shadow.json`](../../provenance/colored-petri-net-shadow.json).

## Implemented surface

The shadow kernel provides immutable generic colored-Petri-net:

- value, token, marking, binding, and nominal identity records;
- graph definitions, guards, inhibitor patterns, and inscriptions;
- structural definition and marking validation;
- pure transition enablement;
- deterministic or explicitly directed binding selection; and
- pure firing results with successor markings and retained audit evidence.

The kernel uses only the Python standard library and relative imports within its package. It performs no persistence, scheduling, task invocation, external effect, scientific calculation, human decision, or acceptance transition.

## Deliberate compatibility treatment

The copied production modules preserve the existing `ksdft2effmass.petrinet.colored.*` identity-domain strings. This is necessary for byte-identical shadow behavior and does not make those strings a Project Koios wire contract. A future production transfer must either retain them through an explicit compatibility policy or introduce a separately versioned identity migration with rollback evidence.

The shadow import surface is `projectkoios.workflow.petrinet.colored`. The retained `specification/workflow-cpn/v1` material in `ksdft2effmass` is historical audit evidence and is not part of this pilot.

## Excluded surfaces

The pilot does not copy or implement:

- `ksdft2effmass.workflows.model` or its CPN adapter;
- WorkflowRun aggregates, replay, persistence, or dispatch control;
- artifacts, normalized observations, or scientific decisions;
- DFT, Quantum ESPRESSO, calculator, integration, analysis, or campaign code;
- the retired v1 Workflow CPN API or schemas;
- a Project Koios core schema; or
- a `ksdft2effmass` consumer migration.

## Validation boundary

Software verification consists of the inherited behavioral suite under the Project Koios import namespace, an adapted dependency-direction check, manifest-bound provenance checks, Ruff, mypy over production source, Python 3.14 package build and installation checks, and byte-identity verification against the selected source revision.

Passing these checks establishes only that the shadow kernel preserves the tested software behavior and source evidence. It does not establish public API stability, serialization compatibility, scientific validation, human acceptance of a production transfer, or readiness to remove the source implementation.

## Transfer gate

Production ownership transfer remains blocked until Project Koios has an accepted core-to-Petri boundary, at least one complete managed-project adapter, an explicit identity and wire-version policy, destination release and rollback plans, consumer shadow-replay evidence, and separate human acceptance of the transfer.
