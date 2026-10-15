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
source-authority reference/revision/evidence identities. It stores no SDK
payload body, owner artifact, machine path, private locator, live repository,
CPN definition, or marking body.

Reservation and commit use `BEGIN IMMEDIATE`, `PRAGMA synchronous = FULL`,
foreign keys, a bounded busy timeout, and rollback-journal mode. One commit
transaction verifies the exact active reservation and predecessor, inserts the
compact commit and ordered evidence references, marks the reservation consumed,
deletes the active reservation, and advances the marking coordinate. Exact
replay is idempotent and distinct replay conflicts. Commit and predecessor
record digests detect corruption before reconstruction. The private database
path rejects symlinks, links, non-private modes, and foreign ownership.

A process-crash test leaves an uncommitted marking update in a separate process
and proves that reopening recovers the prior current reservation. A precommit
fault-injection seam proves that commit rows, evidence references, reservation
consumption, and marking advancement roll back together. Reopening reconstructs
both the compact commit and its source-authority references.

`ExperimentalWorkflowPureActionCommitEventJsonCodec` supplies a strict closed
canonical JSON encoding for that identity-only event, including its exact net
instance. The durable repository retains and verifies the exact bytes against
its typed columns. One closed snapshot read returns coordinates, compact record,
and exact event bytes from one observation and distinguishes found, absent,
incompatible, corrupt, and error outcomes.
`ExperimentalWorkflowPureActionCommittedReplayService` consumes that snapshot,
reconstructs the compact commit identity and full coordinates, and never invokes
an owner, source repository, codec owned by an integration, or CPN firer.

This remains a v0 candidate. Replay of retained definitions, markings, execution
profiles, CPN firing, and full runtime safety state remains incomplete; this
compact structural replay does not claim complete CPN-bindings replay. Backups,
migrations, operational monitoring, and closed read results outside the compact
commit snapshot also remain incomplete. Source revalidation and SQLite commit are
sequential across nominal repositories; production source revision immutability
must close that observation race.
