# projectkoios-workflow

Reusable workflow execution and process/state orchestration for Project Koios.

The repository currently contains a non-authoritative Workflow-owned
colored-Petri-net candidate under `projectkoios.workflow.petrinet.colored`.
It began from the pinned `ksdft2effmass` shadow at revision
`be70e856911456402ea2b2562cd2508d0963e4d9` and now includes owner-authored
canonical transport, control-record, execution-profile, child-plan/export,
deployment-linking, and replay extensions. Exact inherited and owner-authored
file evidence is recorded in
[`provenance/colored-petri-net-shadow.json`](provenance/colored-petri-net-shadow.json).
The candidate remains non-authoritative for provider execution, migration, and
scientific acceptance. Its documented direct-module imports are now an
authorized release-candidate SDK evaluation surface; they are not yet a
published package compatibility promise. Start with the
[SDK quick start](docs/sdk/quickstart.md), use the checked
[operation manifest](docs/sdk/operation-manifest.json) for human or LLM
discovery, follow the [error-handling guide](docs/sdk/error-handling.md), and
apply the [provider conformance profile](docs/sdk/provider-conformance.md) in a
provider repository.

The candidate provides pure definitions, markings, validation, enablement,
deterministic selection, and firing. Review workflow kinds are grouped under
the explicit `projectkoios.workflow.review.{course,reference}` namespace; no
parallel top-level `*_review` packages or initializer facades are provided. A
separate unaccepted
`projectkoios.workflow.core` prototype provides immutable engine-neutral
references, runs, state snapshots, structural preflight, bounded transition
processing, audit evidence, and deterministic replay.

A bounded candidate local runtime slice now composes that core with opaque
compare-and-append persistence, private canonical event records, hardened
single-operator SQLite history, run-scoped request idempotency, reservation,
and effect-free identity-chain replay. Its first pure consumer accepts typed metadata-only
organizer teaching proposals for the non-authorizing
`proposal_observed → course_identity_candidate` transition. It also accepts
complete ingestion-owned reference-evidence and claim-candidate metadata for
the non-authorizing
`reference_evidence_observed → manual_claim_review_required` transition. A
separate, exact human decision record and separately scoped workflow authority
may then record `reviewed_retained` or `reviewed_excluded`. Neither disposition
asserts claim support, scientific acceptance, publication suitability, or
publication authority. PDF parsing, extraction, OCR, transcript content, and
derivation audit remain in `projectkoios-ingestion`. It does not provide a
scheduler, queue, worker, claim, lease, external dispatch, background daemon,
public wire format, API binding, consumer migration, release, or compatibility
promise. See the
[workflow-core proposal](docs/contracts/workflow-core.md), the
[local-runtime candidate contract](docs/contracts/workflow-runtime.md), the
[pilot boundary](docs/pilots/colored-petri-net-shadow.md), and the
[colored-Petri-net reference authority](docs/references/colored-petri-net-authority.md).

Repository routing is documented in `projectkoios-bootstrap/maps/repositories.md`; cross-repository product architecture belongs in `projectkoios`.

## SDK evaluation

Five copyable examples under [`examples/sdk`](examples/sdk) cover definition
validation, enablement/selection/firing, canonical replay, opaque payload
references, and separate child-plan export/linking. CI executes every example
against the built wheel. Package initializers intentionally remain empty;
consumers import from the semantic owner modules recorded in the SDK manifest.

The project version remains `0.0.0` until the provider-owned simulations trial,
independent review, and release gate complete. No package has been published.

## Contracts

Authoritative workflow contract proposals and accepted contracts are indexed
in [`docs/contracts/README.md`](docs/contracts/README.md).
