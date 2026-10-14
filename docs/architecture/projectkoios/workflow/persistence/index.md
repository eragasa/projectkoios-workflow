# `projectkoios.workflow.persistence` architecture

## Responsibility

Persistence owns durable append-only events, definition and plan bytes, marking revisions, token reservations, occurrences, attempts, dispatch outbox records, provenance projections, and integrity verification. It preserves uncertainty rather than converting an acknowledgement failure into absence.

Owner artifacts and private payloads remain outside this store. Workflow retains bounded typed references, hashes, sizes, and sealed locators.
