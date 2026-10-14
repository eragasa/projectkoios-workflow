# WF-ISSUE-0016 — Artifact resolution and operation-identity ownership

- **Kind:** architecture
- **Status:** OPEN
- **Workflow-local scope:** opaque artifact transport, sealed locators, and effect correlation
- **Authoritative owner:** Workflow protocol architecture with artifact/provider owners

## Problem or question

Which component resolves content-addressed artifact references into operational locators, and which component assigns the generic `operation_id` used to correlate staging, execution, evidence, and provenance?

## Current evidence

Workflow must store privacy-reduced typed references rather than private paths. Domain and provider owners retain artifact roles, formats, saved-state semantics, and authority checks. Simulations proposes provider-neutral artifact declarations and collections in `integrations/base`, but no accepted cross-repository resolver interface or operation-identity contract exists.

## Consequence

Resolving artifacts in the control plane would leak provider dependencies and private locators. Allowing providers to invent generic operation identities could break occurrence correlation, idempotency, and replay. Conflating generic operation identity with a native job or artifact identity would make restarts ambiguous.

## Alternatives and recommendation

The current recommendation is that Workflow derive the generic operation/effect identity from the exact plan, occurrence, attempt, and action mapping. Isolated owner/provider workers resolve opaque references under scoped authority and return sealed staging/evidence records. Providers separately assign generation-safe native job and artifact identities. Alternative resolver services remain possible if their ownership, authority, and privacy semantics are explicit.

## Resolution gate

A reviewed protocol covers resolver authentication, authority, content verification, locator sealing, expiry, transfer/staging receipts, operation/native identity separation, redaction, tamper failure, restart, and provenance reconstruction across Ingestion and simulation fixtures.

## Affected architecture

Typed envelopes, action descriptors, worker protocol, lifecycle staging, persistence/provenance, API redaction, and provider registries.
