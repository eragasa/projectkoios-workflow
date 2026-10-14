# WF-ISSUE-0002 — Grant issuer and revocation model

- **Kind:** architecture
- **Status:** OPEN
- **Workflow-local scope:** authority-token admission and retention
- **Authoritative owner:** product authority policy in `projectkoios`, with domain/environment owners

## Problem or question

Who issues, revokes, expires, and records consumption of grants for filesystem, database, network, calculator, cancellation, and publication effects?

## Current evidence

The architecture requires a typed grant reference bound to provider, capability, occurrence, attempt, request/prepared/start digests, executable and inputs, limits, validity, and reuse policy. Workflow must not infer authority from API authentication, historical evidence, or provider capability.

All interactive Project Koios Pi sessions act for the same human operator. Session, worker, agent, and message identities may establish technical provenance and custody, but they are not distinct human principals. Inter-session coordination, review, agreement, or forwarding therefore cannot satisfy independent-human approval, dual control, or operation-specific operator authorization. This clarification neither broadens capabilities nor waives an explicit authorization gate.

## Consequence

Effect admission, cancellation, restart recovery, and provider conformance cannot become accepted contracts.

## Alternatives and recommendation

Alternatives include an owner/environment authority broker, a narrowly scoped Workflow-integrated broker, or externally supplied signed grants. The current recommendation is external issuance with Workflow reservation/audit and immediate provider revalidation.

## Resolution gate

An authoritative policy defines human-principal versus agent/session identity, issuers, signature or lookup scheme, revocation observation, expiry, one-shot consumption, cancellation scope, secret handling, and replay tests. Conformance proves that multiple Pi sessions cannot be counted as multiple human approvers or mint authority by consensus.

## Affected architecture

SDK lifecycle, runtime occurrences, service authentication separation, worker launch, and persistence. [`WF-ISSUE-0012`](WF-ISSUE-0012.md) owns reservation representation; its begin/reservation operation records custody only and cannot satisfy this issue's authority requirement.
