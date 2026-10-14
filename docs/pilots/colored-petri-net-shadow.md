# Colored Petri Net shadow-conformance pilot

## Status

Historical and superseded as the description of the current implementation.
`WORKFLOW-CPN-SHADOW-01` records the original non-authoritative import baseline;
the current working-tree candidate is governed by
[`workflow-cpn-bindings.md`](../contracts/workflow-cpn-bindings.md).

Neither the historical pilot nor the current candidate transfers production
authority, publishes a compatibility promise, migrates a consumer, or
authorizes workflow or scientific execution.

## Source boundary

The original baseline imported production modules from
`ksdft2effmass.petrinet.colored` at clean source revision
`be70e856911456402ea2b2562cd2508d0963e4d9`. The current candidate is no longer
byte-identical: it retains explicitly recorded inherited files and adds or
changes Workflow-owned source and verification. This document must not be used
as evidence of current byte identity.

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

The historical import initially preserved legacy identity domains. The current
candidate uses separately versioned Project Koios identity domains and does not
promise preservation of legacy identity strings. Its aggregate package
initializer exports no facade names; proposed direct semantic-owner modules are
listed in the candidate public-import inventory.

The historical shadow namespace was `projectkoios.workflow.petrinet.colored`. The retained `specification/workflow-cpn/v1` material in `ksdft2effmass` is historical audit evidence and is not part of this pilot.

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
