# QE artifact-set durable pure-action vertical-slice evidence

## Scope

This evidence records one real Simulations-owned pure action traversing the
experimental Workflow authorization, reservation, owner invocation, output
admission, pure CPN firing, durable commit, and replay path. It demonstrates a
bounded owner integration; it does not claim calculator execution, an OS-process
worker sandbox, full execution-plan closure, global scheduler replay, complete
CPN-bindings conformance, production release readiness, or effectful semantics.

## Exact revisions and artifacts

- Workflow repository committed candidate:
  `projectkoios-workflow@4dc9eaa` (`feat: add committed safety-state replay`).
- Simulations branch: `feature/qe-scf-workflow-sdk-pilot`.
- Simulations committed vertical slice:
  `projectkoios-simulations@c69c3fe5a949e631c6201f2f7d92297c90a5eb11`
  (`feat: add durable QE workflow vertical slice`).
- Simulations predecessor SDK pilot:
  `projectkoios-simulations@d7f46384d34237cb6dba2782dbaaf03027482856`.
- Candidate Simulations wheel:
  `projectkoios_simulations-0.1.0.dev0-py3-none-any.whl`.
- Candidate Simulations wheel SHA-256:
  `a7a6a889ad660ab4ad96e452c131ac24cc98a005d36d7526a270da278529c7b9`.
  Two precommit builds and one clean committed-source rebuild with
  `SOURCE_DATE_EPOCH=1791990317` were byte-identical.
- Workflow SDK contract: `projectkoios-workflow-sdk==0.1.0a1`; installed wheel
  SHA-256:
  `925f6974c49c8935ebf2f002b18c86d29375e1b11c3ffc17a29d305fb8095ff4`.
- Experimental full runtime optional pin: `projectkoios-workflow==0.0.0`;
  reproducible wheel SHA-256:
  `d8974031d1e0018ba88c18a4fa39dac3d5bee3658d58d0a8f98d6dbd4a661aad`.

The Simulations extension was committed locally. No push was performed.

## Owner implementation

The Simulations candidate adds:

- `QeScfSavedStateArtifactSetProjectorIntegration`, a nominal SDK worker
  composition root with an immutable deployment-supplied manifest; the executed
  vector uses the exact reproducible Simulations wheel digest above;
- `QeScfSavedStateProjectionRequestSourceRepository`, an outward nominal
  implementation of
  `ExperimentalWorkflowPureActionInputSourceRepository`;
- private `0600` temporary writes and atomic no-replace linking into an
  owner-controlled content-addressed source directory;
- an opaque path-free source identity whose digest is checked against bounded
  repository-loaded bytes;
- exact owner-codec decoding before Workflow source evidence is constructed;
  and
- closed absent, incompatible, corrupt, and error results.

The adapter API never replaces an existing revision. Workflow receives neither
the private filesystem root nor a private locator.

## Executed path

The cross-repository test constructs an actual CPN definition and marking and
executes:

```text
owner request retention
→ exact CPN enablement and deterministic selection
→ repository-authorized SDK request construction
→ durable predecessor reservation
→ validated Simulations worker integration invocation
→ opaque owner-identity output admission
→ pure CPN firing
→ atomic SQLite compact commit + CPN evidence + lifecycle + marking advance
→ compact committed replay
→ durable CPN refiring
→ reservation-lifecycle replay
→ committed safety-state reconstruction
```

The action is the existing
`QeScfSavedStateArtifactSetProjector.action(...)`, not a synthetic Workflow
firer. It performs no calculator or other external effect.

After commit, the test deletes the complete owner source directory. Every replay
still succeeds and a counting owner firer remains at exactly one call. The exact
owner request bytes and canonical artifact-set evidence bytes are absent from
the Workflow SQLite database. The logical artifact-set identity remains in the
successor CPN marking by design.

## Deterministic identities

- selected-binding evidence:
  `3ca155cd09bf8fb0cd921688a894284665bbad7f284df3c1f3bd668644765bd4`;
- source reference:
  `03eb0408eb031e2e951b79a265048219d2c3800b3556576026e441341e75ae39`;
- integration manifest:
  `140197dc0fd386c7c9e433f3ff47c609d5b9ddfef4dd3b3620cecf1d73bf8644`;
- input bindings:
  `ca98772a5cce04065134cdb4d3d57a39712c0c655aab0076b0d75812ca7493e5`;
- SDK request:
  `417d0d912f96acac7a65ff5d42cc85de670d304805a50b859a01123d2162a64d`;
- authorized inputs:
  `a69fcf048f90500b0b35ea7153ccd8e15a1b7553ffd36a9aab0e2d53acb09b3d`;
- CPN plan:
  `3ba808794b16953f3fceb20b9f18b204912582ea6dbe3d36100bf321b81b3411`;
- reservation:
  `38596e52afac8f80438b5e26fdf506f3d41dc4a500a3d40ec8b8be05377fddb6`;
- invocation outcome:
  `b8cf4187884dc9e087ea4de9760e51fd016378cfba7d29ce6f62df275ac7dc52`;
- firing outcome:
  `4fb981884ffee5577ab25cec6e0a940a1137a8a6a99f6707a06fdef6e81288b5`;
- CPN firing result:
  `fa47c1246ee164eab15723cd8fe9ff8ac556259e5939d4db630135911d111ccf`;
- successor marking:
  `70ae79097bc2005a6992057373fbbcc7540b1167f7485d7d29c12945cdb45fb6`;
- compact commit:
  `5c58d4827f77d95a01d52484fc4ac628a385d9984ae8e1adc3db1ea684248df4`;
- compact event SHA-256:
  `f6968d85a163d28563de41a287f37f91a489a88e7bf8f65307d098c68aa1a61a`;
- reserved lifecycle event:
  `2f59dd5b34f32717b6928f27be19b449ede6d9ee2d4418b2daa0bc3e7bdced54`;
- committed lifecycle event:
  `a8fef9583c9dd56558099b8d1e1209164ce04544909ccfe9e2d2a28bcd39a103`.

## Verification

Base Simulations environment:

```text
694 passed, 8 skipped, 202 subtests passed
Ruff check: passed
Ruff format: 436 files already formatted
mypy: success for 231 source files
wheel build and packaged adapter/typing/runtime-extra inspection: passed
reproducible wheel comparison: passed
```

The two runtime-coupled tests are intentionally skipped without the optional
full Workflow runtime. In the explicitly composed cross-repository environment:

```text
2 runtime-coupled tests passed
strict mypy for the owner runtime adapter: passed
20 combined runtime-coupled and SDK owner tests passed
clean cross-wheel `python -I` runtime-coupled suite: 2 passed
clean environment dependency check: 24 installed packages compatible
```

The protected owner domain sources remain unchanged. No QE executable,
subprocess, scheduler, network, staging, or scientific-acceptance operation was
invoked.

## Operational assessment

The slice demonstrates concrete value: Workflow can durably advance CPN state
from a real owner action while keeping private owner payload bodies out of
compact state, and four independent replay views remain usable after the owner
source is unavailable. It also exposes material adoption cost: one owner action
currently requires explicit mapping, input-plan, CPN-plan, manifest,
reservation, invocation, firing, commit, and replay composition.

Further internal infrastructure is not justified by this pilot alone. First
make the durable CPN commit path canonical, then validate the SDK boundary with
a structurally independent owner. Close only the packaging, plan/profile,
source-authority, and worker-isolation gaps those supported owner paths require.
Effectful lifecycle and global scheduler replay remain deferred.
