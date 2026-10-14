# `projectkoios.workflow.service` architecture

## Responsibility

The service is the authenticated control plane. It exposes typed operations for registration, compilation, linking, run creation, signals, approvals, cancellation, claims, leases, provider observations, reconciliation, replay, provenance, health, and readiness.

It coordinates components but does not import or execute domain plugins. Every operation uses `DataObjectActionRequest → DataObjectActionizer → DataObjectActionResult`.
