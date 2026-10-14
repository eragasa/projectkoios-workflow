# `projectkoios.workflow.worker` implementation

## Responsibility

Load plugins through declared entry points only in the worker process. Pin package/environment and executable digests. Enforce payload limits, private workspaces, no shell, process-group closure, bounded resources, redaction, and protocol version negotiation.

A provider-owned durable launch ledger is recommended for start-key deduplication and authoritative reconciliation. Health means the worker process responds; readiness additionally means its registered providers can accept compatible claims.
