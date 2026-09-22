# projectkoios-workflow

Reusable workflow execution and process/state orchestration for Project Koios.

The repository currently contains a non-authoritative colored-Petri-net shadow-conformance pilot under `projectkoios.workflow.petrinet.colored`. Its production source is byte-identical to the generic kernel in `ksdft2effmass` at revision `be70e856911456402ea2b2562cd2508d0963e4d9`; source and transformation evidence is recorded in [`provenance/colored-petri-net-shadow.json`](provenance/colored-petri-net-shadow.json).

The pilot provides pure definitions, markings, validation, enablement,
deterministic selection, and firing. A separate unaccepted
`projectkoios.workflow.core` prototype provides immutable engine-neutral
references, runs, state snapshots, structural preflight, bounded transition
processing, audit evidence, and deterministic replay.

A bounded candidate local runtime slice now composes that core with opaque
compare-and-append persistence, private canonical event records, hardened
single-operator SQLite history, run-scoped request idempotency, reservation,
and effect-free identity-chain replay. Its first pure consumer accepts typed metadata-only
organizer teaching proposals for the non-authorizing
`proposal_observed → course_identity_candidate` transition. It also accepts
complete ingestion-owned reference-evidence metadata for the non-authorizing
`reference_evidence_observed → manual_claim_review_required` transition. PDF
parsing, extraction, OCR, transcript content, and derivation audit remain in
`projectkoios-ingestion`. It does not provide a scheduler, queue, worker, claim,
lease, external dispatch, background daemon,
public wire format, API binding, consumer migration, release, or compatibility
promise. See the
[workflow-core proposal](docs/contracts/workflow-core.md), the
[local-runtime candidate contract](docs/contracts/workflow-runtime.md), the
[pilot boundary](docs/pilots/colored-petri-net-shadow.md), and the
[colored-Petri-net reference authority](docs/references/colored-petri-net-authority.md).

Repository routing is documented in `projectkoios-bootstrap/maps/repositories.md`; cross-repository product architecture belongs in `projectkoios`.

## Contracts

Authoritative workflow contract proposals and accepted contracts are indexed
in [`docs/contracts/README.md`](docs/contracts/README.md).
