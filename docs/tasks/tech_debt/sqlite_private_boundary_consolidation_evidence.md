# SQLite private-boundary consolidation evidence

## Scope

This record covers a behavior-preserving organization slice required before a
durable CPN replay-transcript schema. It adds no schema migration, table, public
repository operation, identity domain, or canonical representation.

## Implemented organization

- `persistence._sqlite_private` now owns absolute-path normalization, secure
  ancestor creation, no-follow availability, symlink and non-directory
  rejection, owner and private-mode checks, regular-file and hard-link checks,
  SQLite connection setup, busy timeout, foreign keys, full synchronous mode,
  rollback-journal enforcement, exact schema inspection/initialization, and
  best-effort rollback.
- Both `SQLiteAtomicRevisionStore` and
  `ExperimentalSQLitePureActionReservationRepository` use that shared boundary
  while retaining their existing public dataclasses, schemas, transaction
  phases, result types, and exception classification.
- `persistence._pure_action_sqlite_rows` owns pure-action nominal
  reconstruction, row encoding/decoding, digest construction and verification,
  and commit-correlation checks. `pure_action_sqlite` retains query ordering,
  transaction orchestration, atomicity, and closed outcome mapping.
- CPN replay bundle records/factory, canonical transcript serialization, and
  pure refiring service are separated into focused execution modules. Public
  exports remain unchanged.
- No provenance-bound shadow CPN source changed. Compact commit events still
  contain identities and admitted authority references only; definitions,
  markings, owner payloads, artifacts, and private locators remain absent.

## Preserved evidence

The unchanged suites continue to cover private directory/file modes, symlink
rejection, exact schema/version rejection, incompatible and corrupt reads,
record and predecessor digest mismatch, canonical event mismatch, reopen,
rollback, process-crash recovery, concurrent single-winner commit, idempotence,
and closed indeterminate/error outcomes.

The canonical CPN transcript remains byte-identical for the deterministic
fixture:

- bundle identity:
  `60ca7e19c47bc8026f178fb97a79f9f9fd8348d38e3f6a1118dc71229ae3d5da`;
- transcript SHA-256:
  `d001410c1f5888d2d31d4a8a81960cbb571b3064d9f51cc9f491be20f0c4b7e4`.

## Validation

Validation from the uncommitted organization candidate on Workflow revision
`dcdde2a`:

- full Workflow suite: `406 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `63` production source files;
- Ruff, changed-source formatting, architecture/documentation checks, runtime
  dependency boundary, shadow provenance, and `git diff --check`: passed;
- two Workflow wheels built with the same `SOURCE_DATE_EPOCH` were
  byte-identical, SHA-256
  `92689a045eb30dde39dfdb3500e704c52456926a6e74d1671114e23ff4c6d4a5`;
- the clean Workflow wheel installed with the standalone SDK wheel and imported
  both SQLite repositories and all public replay components.

Artifact SHA-256 values:

- shared private SQLite policy:
  `7bccde9314b061d47f8b610b8361fa6ae180e93a75ebadd6bf2f070bc79efb3d`;
- pure-action SQLite row codecs:
  `3d09cfb3b37de46c3af4150548a11b2009cb57c602308652c168c29a9b1c1a5b`;
- opaque revision SQLite adapter:
  `c78d9429d5fb049509b9a33351750ab7e9891e44dfe120d2f5714d09c08d15fe`;
- pure-action SQLite orchestration:
  `4e40bd18f847a08f4bee66adafa7cacc4b19971ed2a938dab8222044c42ee149`;
- CPN replay service:
  `98449f4f70df918cb1fda527a0a5d18afad8a5bde5f025496013879706905487`;
- CPN replay bundle models and factory:
  `bff36016e49e7093d597e7a8d06dffe895b0c70cbb9c2a5ee19e5d2b575840e3`;
- CPN replay canonical serialization:
  `17b9bcbc8f5b8a6080552a41d85605f20bfbe5067dd67687281fec62f46d10f6`.

## Remaining boundary

This organization slice does not authorize or implement durable transcript
retention. A later separately reviewed migration may add content-addressed
replay evidence and an atomic compact-commit reference only after defining
closed migration, compatibility, privacy, corruption, and rollback behavior.
