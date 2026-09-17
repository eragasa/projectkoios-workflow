# Architecture Baseline

## Purpose

This document records the current observed architecture.

It is not a list of decisions.

It is not a refactor plan.

It is a baseline for future reviews.

## Observed modules

| area | modules/files | notes |
|---|---|---|
| core/schema | — | Not implemented; the current Petri-net pilot is not Project Koios core schema. |
| runtime | — | Workflow-run runtime, persistence, and dispatch are not implemented. |
| UI | — | Not implemented or owned here. |
| Petri-net/backend | `src/python/projectkoios/workflow/petrinet/colored/` | Non-authoritative, pure shadow kernel bound to an exact `ksdft2effmass` source revision. |
| adapters | — | Core-to-Petri and managed-project adapters are not implemented. |
| tests | `tests/projectkoios/workflow/petrinet/colored/`, `tests/test__ColoredPetriNetShadowProvenance.py` | Inherited behavioral verification, adapted dependency direction, and exact provenance checks. |

## Observed dependency edges

| source | target | status |
|---|---|---|
| `petrinet.colored` modules | sibling `petrinet.colored` modules | intended internal relative imports |
| `petrinet.colored` | Python standard library | intended |
| `petrinet.colored` | Project Koios core/runtime/adapters/applications | prohibited and tested absent |

## Known problems

| id | area | issue | status | next action |
|---|---|---|---|---|
| D-001 | identity | Byte-identical shadow code retains `ksdft2effmass.petrinet.colored.*` identity-domain strings. | intentional shadow limitation | Decide compatibility and version migration before production transfer. |
| D-002 | core boundary | No Petri-independent Project Koios core schema exists. | open | Define and accept the core contract before adding an adapter. |
| D-003 | consumer migration | No managed research project consumes the shadow package. | open | Build a separately reviewed adapter and shadow replay before transfer. |

## Current target assumption

The working assumption is:

Core schema should remain independent of runtime, UI, Petri-net backends, process-mining libraries, and external adapters.

This assumption can be changed only by human decision.
