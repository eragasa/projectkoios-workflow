# Colored Petri Net Reference Authority

- **Document type:** Reference and conformance note
- **Status:** Proposed reference baseline
- **Scope:** Project Koios workflow specifications
- **Date:** 2026-09-15

## Purpose

Project Koios needs an external authority for the meaning of a colored Petri net
before adopting or extracting the implementation incubated in
`ksdft2effmass.petrinet.colored`.

Selecting a reference does not claim that the current implementation conforms to
the reference, ISO/IEC 15909-1, or CPN Tools. A conformance claim requires an
explicit profile, construct mapping, divergence register, and behavioral tests.

## Primary formal reference

The primary reference is:

> Kurt Jensen and Lars M. Kristensen, *Coloured Petri Nets: Modelling and
> Validation of Concurrent Systems*, Springer, 2009,
> <https://doi.org/10.1007/b95112>.

Chapter 3, **Formal Definition of Non-hierarchical Coloured Petri Nets**, pages
79--94, is the initial formal authority for the core model. Chapters 2 and 3
should be read together because Chapter 2 introduces the constructs used by the
formal definition.

This book is preferable to a tutorial as the primary source because it gives
formal definitions after the introductory examples and distinguishes
non-hierarchical, hierarchical, state-space, and timed CPN concepts.

## Standards-level reference

The standards-level reference is:

> ISO/IEC 15909-1:2019, *Systems and software engineering---High-level Petri
> nets---Part 1: Concepts, definitions and graphical notation*,
> <https://www.iso.org/standard/67235.html>.

The standard defines syntax and semantics for high-level Petri nets and provides
a common reference for specifications and tool interoperability. It is broader
than the exact Project Koios CPN subset. Project Koios should claim ISO
conformance only after a clause-level mapping and appropriate conformance
evidence exist.

## Tooling reference

For CPN Tools terminology and implementation context, use:

> Kurt Jensen, Lars Michael Kristensen, and Lisa Wells, “Coloured Petri Nets
> and CPN Tools for Modelling and Validation of Concurrent Systems,”
> *International Journal on Software Tools for Technology Transfer* 9,
> 213--254 (2007), <https://doi.org/10.1007/s10009-007-0038-x>.

Project Koios does not currently implement the CPN Tools inscription language,
file format, GUI, Standard ML environment, state-space tooling, or timed and
hierarchical feature set. This article is therefore contextual rather than a
compatibility contract.

Machine-readable citations are retained in
`provenance/colored-petri-nets.bib`.

## Required Project Koios profile

Before production extraction, Project Koios should publish a narrow profile
that maps each supported construct to the primary formal reference.

At minimum, the profile should define:

- color sets and admitted token values;
- typed places and markings as multisets;
- transition variables and bindings;
- guards and their expression domain;
- input, output, read, test, and inhibitor behavior, where supported;
- transition enabledness;
- token consumption and production;
- firing and successor-marking semantics;
- concurrent versus conflicting bindings;
- nondeterminism in the formal model;
- any deterministic selection policy imposed by the runtime; and
- unsupported hierarchical, timed, or state-space constructs.

## Core semantics versus platform policy

The extracted package must distinguish formal CPN semantics from Project Koios
execution policy.

| Concern | Classification |
|---|---|
| Typed places, tokens, multisets, transitions, bindings, guards, and firing | Candidate core CPN semantics |
| Restricted expression language instead of unrestricted Standard ML | Project Koios profile restriction |
| Deterministic choice among multiple enabled bindings | Runtime selection policy, not intrinsic CPN semantics |
| Stable object identities, revisions, and content hashes | Project Koios representation extension |
| External result injection and output correlation | Workflow adaptation extension |
| Audit records and evidence identities | Project Koios provenance extension |
| Human authority and execution grants | Scientific control-plane policy |
| Retry budgets and remediation | Workflow policy layered above the CPN model |

A deterministic selector must not redefine enabledness. The formal model may
admit several enabled binding elements even when the execution layer chooses one
through a reproducible policy.

## Conformance vocabulary

Until the mapping is complete, documentation should say that the implementation
is a **restricted colored-Petri-net model informed by Jensen and Kristensen**.

The following claims require increasing evidence:

1. **CPN-informed** — uses concepts from the cited formalism.
2. **Project Koios CPN profile implementation** — implements an explicit,
   versioned subset with documented extensions.
3. **Conformant to the Project Koios CPN profile** — passes the complete profile
   conformance suite.
4. **ISO/IEC 15909-1 conformant** — requires a separate standards mapping and
   evidence; profile conformance alone is insufficient.
5. **CPN Tools compatible** — requires exact language and interchange behavior;
   no such compatibility is currently claimed.

## Extraction consequence

The reference baseline strengthens the case for a shadow extraction of
`ksdft2effmass.petrinet.colored`, but does not authorize a source move. The
shadow pilot should first produce:

1. a construct-by-construct mapping to Jensen and Kristensen;
2. a register of restrictions and extensions;
3. tests derived from independently stated formal examples;
4. separation of enabledness from deterministic selection policy; and
5. explicit non-conformance statements for unsupported constructs.

Only then should Project Koios decide whether the resulting profile is a stable
public contract for `projectkoios-workflow`.
