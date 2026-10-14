# WF-ISSUE-0001 — Stable base-contract packaging

- **Kind:** architecture
- **Status:** OPEN
- **Workflow-local scope:** SDK dependency boundary
- **Authoritative owner:** cross-repository packaging decision in `projectkoios`

## Problem or question

Which stable distribution owns `DataObjectActionRequest`, `DataObjectActionizer`, `DataObjectActionResult`, and the smallest shared immutable-data contract required by the Workflow SDK?

## Current evidence

The canonical action classes are currently in `/Users/eugene/repos/projectkoios/src/python/projectkoios/base.py`. `projectkoios-workflow/pyproject.toml` declares no runtime dependency. Binding the SDK to the full aggregate package could couple unrelated application concerns into providers and the control plane.

Owner refactoring has also surfaced possible universal source identity, type, and policy primitives. `projectkoios` is evaluating that boundary using Ingestion and other owner evidence. A provisional flattened `projectkoios-ingestion/ingestion/source` diff was stopped and is not accepted evidence for a Workflow dependency. A subsequent one-class `ContentFingerprint` Base proposal was rejected as too narrow, and no Base implementation is proceeding from it. Workflow must neither define nor duplicate these domain/value primitives or freeze assumptions while a coherent cross-owner action/type/identity/policy foundation is being redefined. If `projectkoios` later accepts universal forms, Workflow may reference their exact versions as token colors or action-contract inputs without owning their semantics.

## Consequence

SDK packaging, provider dependency direction, release compatibility, and isolated-worker installation cannot be finalized.

## Alternatives and recommendation

Alternatives are a minimal `projectkoios-contracts` distribution, the existing `projectkoios` distribution, or a deliberately versioned protocol copy. The current recommendation is a minimal authoritative contracts distribution, subject to product-level ownership review.

## Resolution gate

A durable `projectkoios` packaging decision names the owner, public import path, version policy, migration path, and compatibility tests. It separately classifies universal action/data bases from domain-owned source identity/type/policy values, and supplies accepted revisions before Workflow adds any dependency.

## Affected architecture

`projectkoios.workflow.sdk`, provider packages, service packaging, and every typed service operation.
