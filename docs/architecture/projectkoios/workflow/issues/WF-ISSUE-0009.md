# WF-ISSUE-0009 — References provider-action readiness

- **Kind:** dependency
- **Status:** BLOCKED_BY_DEPENDENCY
- **Workflow-local scope:** typed action coverage for References-bound transitions
- **Authoritative owner:** `projectkoios-references`

## Problem or question

Which References domain operations still require stable workflow-facing request/actionizer/result envelopes while preserving owner-owned atomic consistency boundaries?

## Current evidence

Read-only inventory at `e90ba572ed0fb48e990073eb21e9f78165c502af` found typed reducers and actions alongside helper/CLI-only bibliography, graph, catalog, asset, acquisition, Crossref, identity/review, validation, and intake operations. Asset apply and catalog migration must remain owner-atomic composite actions rather than being split for orchestration convenience. No complete schema-5 rebuild action currently exists.

## Consequence

References CLI/composite retirement, human-decision workflows, and clean rebuild equivalence cannot be claimed.

## Alternatives and recommendation

References should publish stable bounded composite actions matching its transaction and authority boundaries. Workflow should bind those actions to CPN transitions and retain only dependency expectations, exact owner revisions, and evidence links.

## Resolution gate

Accepted owner contracts cover the selected migration definitions; same-store and independent-store matrices pass; authority and partial-effect behavior remain unchanged; a durable owner record identifies each resolved gap.

## Affected architecture

Action bindings, approval fragments, migration definitions, provenance, and external dependency reporting.
