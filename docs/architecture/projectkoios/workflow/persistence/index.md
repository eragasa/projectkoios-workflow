# `projectkoios.workflow.persistence` architecture

## Responsibility

Persistence owns durable append-only events, definition and plan bytes, marking revisions, token reservations, occurrences, attempts, dispatch outbox records, provenance projections, and integrity verification. It preserves uncertainty rather than converting an acknowledgement failure into absence.

Owner artifacts, private payloads, and private locators remain outside this
store. Workflow retains only bounded typed references and content identities.

The experimental SQLite pure-action repository is a purpose-built durable
candidate for predecessor reservation and atomic pure-firing commit. It does not
claim complete event history or committed replay.
