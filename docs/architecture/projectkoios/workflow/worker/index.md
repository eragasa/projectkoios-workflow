# `projectkoios.workflow.worker` architecture

## Responsibility

Workers host external SDK implementations in isolated pinned environments. They register capability manifests, claim compatible occurrences, heartbeat leases, invoke typed action or lifecycle providers, and return bounded evidence.

Workers cannot select transitions, mutate markings, alter plans, mint domain authority, or decide retry policy. Loss of a worker after possible effect entry triggers reconciliation rather than redispatch.
