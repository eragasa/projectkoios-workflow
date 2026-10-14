# WF-ISSUE-0006 — SDK and wire compatibility policy

- **Kind:** contract
- **Status:** OPEN
- **Workflow-local scope:** SDK, provider protocol, API, and retained-run interpretation
- **Authoritative owner:** Workflow public-contract governance

## Problem or question

What versioning, negotiation, support-window, schema-evolution, deprecation, and compatibility rules apply across SDK records, manifests, compiled plans, worker protocol, API envelopes, and event subscriptions?

## Current evidence

Runs must pin exact definition, action, provider, environment, compiler, and protocol digests. Installation may need ranges, while replay must never float to a newer interpretation. Current repository version `0.0.0` provides no compatibility promise.

## Consequence

Provider upgrades, retained replay, Applications clients, Web status components, and Laptop BOMs cannot evolve independently with confidence.

## Alternatives and recommendation

Alternatives include strict exact-version lockstep, bounded major/minor ranges with exact run pins, or explicit compatibility adapters. The recommendation is versioned schemas and protocol ranges at registration, exact descriptor pins at plan/link/run time, and additive readers for retained histories.

## Resolution gate

A contract policy defines semantic-version meaning, supported ranges, canonical serialization changes, deprecation duration, adapter ownership, and conformance matrices.

## Affected architecture

All SDK packages, compiler, registry, service/API, worker, visualization, and deployment BOM.
