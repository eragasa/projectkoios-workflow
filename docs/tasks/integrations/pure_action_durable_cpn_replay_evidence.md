# Pure-action durable CPN replay evidence

## Status

Implemented as a bounded v0 experimental candidate.

## Scope

- [x] Preserve compact commit-event bytes and identities.
- [x] Add transactional SQLite format version 2 to version 3 migration.
- [x] Retain canonical replay bundles by content identity in separate tables.
- [x] Link bundle evidence to compact commit, reservation consumption, and
  marking advancement in one transaction.
- [x] Provide no standalone post-commit evidence-link operation.
- [x] Preserve legacy commits with a closed absent-evidence result.
- [x] Verify row digests, bundle digest, canonical decoding, and compact-commit
  correlations on read.
- [x] Distinguish found, absent, incompatible, corrupt, and error reads.
- [x] Refire through only the existing pure CPN replay service.
- [x] Cover reopen, idempotence, concurrency, rollback, migration rollback,
  legacy history, and corruption.

## Follow-up orchestration

The separately reviewed
[durable CPN commit orchestration](pure_action_durable_cpn_commit_orchestration_evidence.md)
now constructs evidence internally from an exact firing candidate and invokes
this atomic port through the authoritative commit path.

## Exclusions

This does not reconstruct complete SDK request/result/evidence history,
reservation lifecycle, owner state, or runtime safety state. It does not invoke
owners or source repositories during replay and does not claim complete
CPN-bindings conformance.

## Evidence

See [validation evidence](pure_action_durable_cpn_replay_evidence_validation.md).
