# projectkoios-workflow

Reusable workflow execution and process/state orchestration for Project Koios.

The repository currently contains a non-authoritative colored-Petri-net shadow-conformance pilot under `projectkoios.workflow.petrinet.colored`. Its production source is byte-identical to the generic kernel in `ksdft2effmass` at revision `be70e856911456402ea2b2562cd2508d0963e4d9`; source and transformation evidence is recorded in [`provenance/colored-petri-net-shadow.json`](provenance/colored-petri-net-shadow.json).

The pilot provides pure definitions, markings, validation, enablement, deterministic selection, and firing. It does not yet provide Project Koios core schema, workflow-run persistence, dispatch, external execution, a public wire format, a consumer migration, a release, or a compatibility promise. See the [pilot boundary](docs/pilots/colored-petri-net-shadow.md) and the [colored-Petri-net reference authority](docs/references/colored-petri-net-authority.md).

Repository routing is documented in `projectkoios-bootstrap/maps/repositories.md`; cross-repository product architecture belongs in `projectkoios`.
