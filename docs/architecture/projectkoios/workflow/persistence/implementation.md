# `projectkoios.workflow.persistence` implementation

## Responsibility

The initial local deployment may use private SQLite plus a private content-addressed blob store. Preserve confinement, no-follow paths, ownership/mode checks, full durability, foreign keys, CAS, exact idempotency, corruption detection, and explicit indeterminate commit status from the current persistence prototype.

The production schema must be purpose-built rather than storing the whole
platform in the existing opaque revision table. Backups require a drained,
quiescent, schema-aware operation; state history is never rolled back.

## Experimental pure-action SQLite repository

`ExperimentalSQLitePureActionReservationRepository` implements the nominal
pure-action reservation repository with a purpose-built private SQLite schema.
It persists immutable initial predecessor coordinates, current predecessor
coordinates, active reservations, consumed reservation identities, complete
compact commit fields, exact canonical commit-event bytes, and ordered
source-authority reference/revision/evidence identities. Compact commit state
stores no SDK payload body, owner artifact, machine path, private locator, live
repository, CPN definition, or marking body. Format version 3 separately stored
content-addressed canonical CPN replay bundles and commit-to-bundle evidence
links; those transcript rows contain the bounded definition and marking bytes
needed for pure refiring. Format version 4 adds ordered, identity-only canonical
reservation-lifecycle events and explicit partial markers for older consumed
reservations whose complete reservation fields cannot be reconstructed.

Both SQLite adapters now use one internal private-database boundary for absolute
path normalization, no-follow creation, ancestor/file type checks, ownership and
mode enforcement, hard-link rejection, connection setup, bounded busy timeout,
foreign keys, `PRAGMA synchronous = FULL`, and rollback-journal enforcement.
Adapter-specific schemas and transactions remain separately owned.

Reservation and commit use `BEGIN IMMEDIATE`. One commit
transaction verifies the exact active reservation and predecessor, inserts the
compact commit and ordered evidence references, marks the reservation consumed,
deletes the active reservation, and advances the marking coordinate. Exact
replay is idempotent and distinct replay conflicts. Commit and predecessor
record digests detect corruption before reconstruction. Compact commit and CPN
replay-evidence row encoding, nominal reconstruction, digest verification, and
correlation checks are separated into focused internal row-codec modules. Exact
schema declarations and the transactional v2-to-v3-to-v4 migrations are also
isolated from repository query ordering and transaction orchestration. Existing
closed fault codes remain unchanged.

A process-crash test leaves an uncommitted marking update in a separate process
and proves that reopening recovers the prior current reservation. A precommit
fault-injection seam proves that commit rows, evidence references, reservation
consumption, marking advancement, canonical replay-bundle retention, and its commit link roll
back together. Reopening reconstructs both the compact commit and its
source-authority references. A transactional version-2-to-version-3 migration
adds only the transcript tables; legacy commits remain valid and return the
closed absent-evidence outcome.

`ExperimentalWorkflowPureActionCommitEventJsonCodec` supplies a strict closed
canonical JSON encoding for that identity-only event, including its exact net
instance. The durable repository retains and verifies the exact bytes against
its typed columns. One closed snapshot read returns coordinates, compact record,
and exact event bytes from one observation and distinguishes found, absent,
incompatible, corrupt, and error outcomes.
`ExperimentalWorkflowPureActionCommittedReplayService` consumes that snapshot,
reconstructs the compact commit identity and full coordinates, and never invokes
an owner, source repository, codec owned by an integration, or CPN firer.

Reservation acceptance retains its complete canonical reserved event in the
same transaction. Commit acceptance appends its commit-bound lifecycle event in
the transaction that retains compact state and CPN evidence, consumes the
reservation, and advances the marking. Version-3 active reservations migrate to
complete reserved histories; consumed version-3 reservations are classified as
legacy partial without fabricated fields. Atomic lifecycle reads verify event
bytes, digests, sequence, and compact-commit correlation.

The separate durable replay-evidence read verifies its row and bundle digests,
correlates CPN-plan, firing-result, predecessor, and successor identities with
the referenced compact commit in one database observation, and distinguishes
found, absent, incompatible, corrupt, and error outcomes. Durable replay then
passes only the canonical bundle bytes to the pure CPN replay service; it does
not invoke owners or source repositories.

This remains a v0 candidate. Complete request/result/evidence history,
reservation-lifecycle reconstruction, and full runtime safety state remain
incomplete; neither compact structural replay nor bounded CPN refiring claims
complete CPN-bindings replay. Backups, later migrations, and operational
monitoring remain incomplete. Source revalidation and SQLite commit are
sequential across nominal repositories; production source revision immutability
must close that observation race.
