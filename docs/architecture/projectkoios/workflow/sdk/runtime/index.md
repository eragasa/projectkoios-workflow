# `projectkoios.workflow.sdk.runtime` architecture

> **Status: provisional architecture candidate.** Record names and field layout
> remain subject to protocol and replay review.

## Responsibility

The SDK runtime module contains immutable context and evidence records exchanged between the control plane and isolated workers. It exposes the identity of a CPN occurrence and one attempt without exposing a mutable marking, scheduler, repository, or provider-selection mechanism.

Protocol keys derive from definition, net instance, transition, binding, occurrence, and attempt identities. Application-facing task names may be projected for users but are not persistence or idempotency authority.
