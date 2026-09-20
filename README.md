# projectkoios-workflow

Reusable workflow execution and process/state orchestration for Project Koios.

The repository currently contains a non-authoritative colored-Petri-net shadow-conformance pilot under `projectkoios.workflow.petrinet.colored`. Its production source is byte-identical to the generic kernel in `ksdft2effmass` at revision `be70e856911456402ea2b2562cd2508d0963e4d9`; source and transformation evidence is recorded in [`provenance/colored-petri-net-shadow.json`](provenance/colored-petri-net-shadow.json).

The pilot provides pure definitions, markings, validation, enablement,
deterministic selection, and firing. A separate unaccepted
`projectkoios.workflow.core` prototype provides immutable engine-neutral
references, runs, state snapshots, bounded transition processing, audit
evidence, and deterministic replay. It does not provide persistence, dispatch,
external execution, a public wire format, consumer migration, a release, or a
compatibility promise. See the
[workflow-core proposal](docs/contracts/workflow-core.md), the
[pilot boundary](docs/pilots/colored-petri-net-shadow.md), and the
[colored-Petri-net reference authority](docs/references/colored-petri-net-authority.md).

Repository routing is documented in `projectkoios-bootstrap/maps/repositories.md`; cross-repository product architecture belongs in `projectkoios`.

## Contracts

Authoritative workflow contract proposals and accepted contracts are indexed
in [`docs/contracts/README.md`](docs/contracts/README.md).
