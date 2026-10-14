# WF-ISSUE-0004 — Exact success-layer contracts

- **Kind:** contract
- **Status:** NARROWED
- **Workflow-local scope:** lifecycle outcomes and CPN result admission
- **Authoritative owner:** Workflow for generic layers; domain owners for normalization and acceptance

## Problem or question

How are process mechanics, provider evidence completeness, normalized domain validity, scientific acceptance, and human/publication approval represented without collapsing them into one success flag?

## Current evidence

The retained VASP fixture has process return code zero while calculation completion is false. Current architecture agrees on separate layers: provider mechanical terminal evidence, action-specific normalization, domain/scientific decision, and separate human authority.

## Consequence

Without exact contracts, downstream transitions could consume incomplete output or misrepresent mechanical completion as scientific acceptance.

## Alternatives and recommendation

The separation itself is the current recommended invariant. Open details include color/result names, whether normalization is always a separate transition, and which evidence completeness checks are generic versus provider-owned.

## Resolution gate

Versioned request/result and color contracts reproduce QE/VASP success and incomplete cases, convergence loops, failure routing, and human approval without ambiguous status conversion.

## Affected architecture

Lifecycle, transition action bindings, domain fragments, provenance, status API, and visualization.
