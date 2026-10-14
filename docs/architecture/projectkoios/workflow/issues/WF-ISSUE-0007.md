# WF-ISSUE-0007 — Event-store, backup, and schema evolution

- **Kind:** architecture
- **Status:** OPEN
- **Workflow-local scope:** durable local service state
- **Authoritative owner:** Workflow persistence architecture and Laptop deployment policy

## Problem or question

What production schema, journal mode, blob layout, backup protocol, migration mechanism, and rollback compatibility support durable CPN state on the laptop?

## Current evidence

The existing SQLite revision store demonstrates private-path hardening, CAS, exact idempotency, full synchronization, integrity framing, and indeterminate acknowledgement. It does not model definitions, markings, reservations, occurrences, attempts, outbox, subscriptions, or provenance as production records.

## Consequence

Service concurrency, crash recovery, backup, deployment rollback, event retention, and projection rebuild remain unspecified.

## Alternatives and recommendation

Alternatives include a purpose-built private SQLite event store, another embedded transactional store, or a separately managed database. SQLite remains the leading laptop candidate, contingent on concurrency, WAL/backup, corruption, and schema-migration evidence.

## Resolution gate

A reviewed schema and migration plan pass crash injection, projection rebuild, quiescent backup/restore verification, forward/rollback compatibility, private-mode checks, and state-history nonrollback guarantees.

## Affected architecture

Persistence, service transactions, outbox, runtime replay, Laptop operations, and API readiness.
