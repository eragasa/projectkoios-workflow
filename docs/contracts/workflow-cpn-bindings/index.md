# Canonical CPN payload and hierarchical binding contract set

## Contract metadata

| Field | Value |
|---|---|
| Contract ID | `projectkoios.workflow.cpn-bindings` |
| Target version | `0.1.0` |
| Status | Proposed architecture contract; no implementation binding |
| Specification revision | Git commit containing this document |
| Owner | `projectkoios-workflow` |
| Acceptance authority | Project Koios operator after workflow-owner and materially affected adapter/consumer review |
| Dependencies | `projectkoios.workflow.core@0.1.0` (Proposed); `projectkoios.workflow.runtime@0.1.0` (Candidate) |
| Consumers | CPN compiler and runtime adapters; managed-project adapters; child-workflow providers |
| Implementation bindings | None |
| Compatibility | Unknown while proposed |
| Effective baseline | None while proposed |

## Status

This document specifies the owner-side architecture required for canonical CPN
payload references and runtime nesting of separately owned child workflows. It
is a proposal, not an available Python API, implementation authorization,
dependency authorization, provider migration, execution grant, release, or
compatibility promise.

The existing `projectkoios.workflow.petrinet.colored` package is a
non-authoritative shadow kernel. It supplies useful evidence for immutable flat
CPN definitions, markings, enablement, selection, and pure firing, but it does
not implement this contract. In particular, its current `CpnValue` model admits
only scalar values and a string sequence, and its current `CpnValueExpression`
admits only literals and whole variables. It does not implement the bounded
control-record, field-projection, or record-construction contract below. The
current local runtime implements only its bounded effect-free Slice A and does
not implement child launch, payload resolution, attempts, dispatch,
cancellation, reconciliation, or quiescence.

## Normative scope and vocabulary

The normative contract begins at **Architectural decision** and continues
through **Stop conditions**, except text explicitly labeled informative,
example, rationale, current evidence, or deferred decision.

The capitalized words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**,
**SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and
**OPTIONAL** have their meanings from the Project Koios contract-governance
policy.

Names in backticks identify required conceptual records and operations. Their
final source modules and class names MAY change before acceptance only if an
explicit mapping preserves every field, invariant, and conformance vector in
this document. No consumer may treat these names as currently importable.

## Purpose

A managed-project CPN needs to carry references to owner-defined typed records
without embedding arbitrary JSON or importing domain classes into the generic
kernel. It also needs to invoke an authoritative child workflow without copying
that child's topology into the parent or creating a hidden imperative task
engine.

This contract defines:

- content-addressed references to immutable owner payloads;
- the boundary between generic CPN token values and owner codecs;
- the definition-closure binding from CPN colors to payload schemas;
- runtime nesting of separately compiled flat child CPNs;
- exact parent/child occurrence, attempt, authority, outcome, primary terminal
  payload, companion evidence, and delivery correlation;
- persistence, replay, cancellation, reconciliation, and quiescence rules; and
- a generic retained staging-receipt barrier for provenance-sensitive effects.

It does not define scientific schemas, calculator formats, artifact-store
implementation, provider-native job identity, or managed-project acceptance
policy.

## Normative contract map

The normative architectural decision formerly presented as one continuous
contract is partitioned below by owned boundary. This split changes document
organization only: all component rules, conformance vectors, acceptance gates,
deferred decisions, and stop conditions remain part of the same umbrella
contract `projectkoios.workflow.cpn-bindings`.

| Component | Owned boundary |
|---|---|
| [Execution profile](execution-profile.md) | Flat CPN semantics, semantic closure, definition representation, and execution-profile identity |
| [Control records](control-records.md) | Bounded control records, field projection, construction, and the no-callback kernel boundary |
| [Payload references](payload-references.md) | Content-addressed owner payload references, canonical encoding, codecs, and assembly |
| [Payload/color bindings](payload-color-bindings.md) | Admission of payload-reference identities into declared CPN string colors |
| [Child exports](child-exports.md) | Separately compiled child definitions and typed ports |
| [Terminal delivery](terminal-delivery.md) | Classification-specific primary payload and companion-evidence requirements |
| [Hierarchical bindings](hierarchical-bindings.md) | Parent/child plan linkage and child-instance identity |
| [Runtime protocol](runtime-protocol.md) | Nested-route sequencing, correlation, cancellation, late delivery, and quiescence |
| [Authority and staging](authority-and-staging.md) | Protected-effect authority, resolution, and staging-receipt barriers |
| [Persistence and replay](persistence-and-replay.md) | Retained evidence and complete replay requirements |
| [Conformance](conformance.md) | Ownership, consumer reconciliation, fixtures, gates, deferred decisions, and stop conditions |

A reader or implementation claiming this umbrella contract MUST apply every
component relevant to its scope and every cross-component identity,
correlation, acceptance, and stop rule. Component files are not independent
compatibility promises.
