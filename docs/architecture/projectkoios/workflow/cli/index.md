# `projectkoios.workflow.cli` architecture

## Responsibility

The CLI is an operator adapter over the authenticated Workflow client. It exposes definition validation/registration, provider status, run inspection and signals, cancellation, replay, provenance, service health/readiness, drain, and backup operations.

It contains no workflow semantics, direct provider invocation, shell execution facility, or credential material beyond a reference to local API authentication.
