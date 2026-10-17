# `ksdft2effmass` workflow capability migration assessment

## Status and scope

This assessment starts the authorized migration of reusable workflow capability
from `ksdft2effmass` to `projectkoios-workflow`. It selects a lean sequence:
retain only evidence-bound compatibility, use existing Workflow contracts where
they fit, and deprecate legacy KSD runtime overgrowth instead of promoting it.

It authorizes no calculator execution, retained-history rewrite, destructive KSD
deletion, package release, tag, or artifact upload. The initial KSD dependency
and import mutation remains a downstream operation coordinated from the KSD
repository.

## Exact inspection boundary

| Repository | Exact revision | Worktree observation |
| --- | --- | --- |
| Workflow | `334c6476277d5c9f1d87d44b0ccab37e41c2ec4e` | Clean and equal to `origin/master` before this assessment slice |
| KSD | `5aaff25b784c7d1bc079a3030a73be387dc11a0f` | Whole worktree heavily dirty; bounded `workflows`, `petrinet/colored`, persistence, tests, and named architecture sources match committed `HEAD`, which equals its tracked branch |
| Simulations production baseline | `c69c3fe5a949e631c6201f2f7d92297c90a5eb11` | Read-only coordination input |
| Simulations test/CI descendant | `4f05789d63f4cb2851c1e4f0ee0d6666e1875a67` | Read-only coordination input |

The KSD migration crosswalk was written against
`2f30d7a37eab8306c7c17da0e2b316d63da8c74c`. Git reports no change from that
revision through `5aaff25b...` in the KSD workflow, CPN, or shared-persistence
source subtrees. This makes the current committed source readable evidence, but
does not make unrelated dirty experiment files an authorized source pin.

Observed implementation size is substantial:

- `python/src/ksdft2effmass/workflows/`: 27,643 lines;
- `python/src/ksdft2effmass/petrinet/colored/`: 4,055 lines;
- `python/src/ksdft2effmass/persistence/`: 1,452 lines; and
- corresponding workflow, CPN, and persistence software-verification tests:
  42,689 lines across 295 Python files.

Size and test volume are not retention evidence. Seventeen production modules
outside the KSD workflow and CPN packages import a bounded subset of workflow
symbols. A repository scan found no committed non-test
`ksdft2effmass.workflow-run:1` payload or WorkflowRun SQLite database. Test
fixtures and documentation do not by themselves justify retaining an active
runtime. Configured external or untracked stores remain unknown and must be
inventoried before destructive deletion.

## Ownership rules

- Workflow owns generic CPN execution, occurrence and attempt coordination,
  authorization, scheduling, persistence, reconciliation, cancellation,
  delivery, and operational replay only where an accepted Workflow contract
  exists.
- KSD owns scientific definitions, calculator and campaign policy, scientific
  observations and acceptance, owner codecs, artifact semantics, retained
  scientific provenance, and direct typed APIs.
- Simulations retains calculator-neutral and provider-specific scientific
  contracts. Workflow must not create competing calculator request, artifact,
  observation, or provider-resource schemas.
- Existing modern Workflow contracts take precedence over porting a conflicting
  KSD abstraction. Unsupported KSD internals are deletion candidates, not
  automatic upstream requirements.
- A retained-history reader is an archive boundary. It does not remain an
  active scheduler, effect executor, or public runtime merely because old bytes
  can be decoded.

## Tranche-based owner map

### Tranche A — exact CPN ownership evidence

**Disposition:** already implemented upstream; formalize current-consumer parity
without changing production behavior.

The KSD and Workflow CPN packages contain nine byte-identical Python source
files. The Workflow package exports the same 68 full-name symbols and preserves
the explicit `ksdft2effmass.petrinet.colored` implementation identity values.
Both repositories carry byte-identical 11,357-byte Apache-2.0 license text with
SHA-256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.
Workflow already retains 73 namespace-transformed KSD test files. The original
shadow-provenance manifest remains immutable historical provenance.

This tranche adds a separate current-consumer parity manifest and test. It
claims source bytes, public-symbol inventory, explicit identity-value and license
parity, and the absence of owner/runtime absolute imports from the generic
kernel only. It does not claim Python `__module__`, pickle, wire-format,
package-release, or dependency-pin compatibility.

### Tranche B — downstream CPN compatibility re-exports

**Owner:** KSD compatibility package, consuming Workflow.

Replace the nine duplicated KSD implementation bodies with root and direct
submodule re-exports of `projectkoios.workflow.petrinet.colored`. Preserve:

- the old `ksdft2effmass.petrinet.colored` root import;
- all currently imported direct submodule routes;
- all 68 public names;
- object identity between old-route and upstream-route symbols; and
- all explicit `ksdft2effmass...` identity values.

After dual-route and consumer checks pass, delete the duplicated 4,055
implementation lines. Do not promise `__module__` or pickle compatibility.
There is no repository evidence that either is a supported persistence format.

This is the smallest implementation slice and the first actual duplicate-code
removal. It does not require a new Workflow production API. It does require a
separately reviewed exact Workflow dependency/source pin in KSD and must cover
`workflows/persistence.py`, which imports CPN direct submodules.

### Tranche C — owner-domain contracts retained downstream

These are current production dependencies or scientific owner policy and must
not be generalized merely to reduce KSD line count:

| KSD capability | Retention |
| --- | --- |
| `workflows/artifacts.py` identities, manifests, producer provenance, and imported-fixture records used by campaigns, QE, and analysis | Keep KSD-owned until a separately evidenced cross-owner intersection exists. Artifact meaning and scientific provenance remain downstream. |
| `workflows/observations.py` and `NormalizedObservationSet` | Keep downstream. Normalization and observation semantics are scientific policy. |
| QE task, process, execution, diagnostic, native-result, and result-value contracts | Keep in the QE owner. Coordinate with Simulations rather than moving them into Workflow. |
| Campaign compositions, `_plane_wave_study`, bulk-silicon policy, and DFT scientific topology | Keep downstream. Workflow may execute a compiled plan but does not own the topology or acceptance policy. |
| `workflow-result:1`, `qe-result-value:1`, and `qoi-result-value:1` owner codecs with actual consumers | Keep owner-controlled. They may support a bounded archive reader; they are not generic Workflow payload schemas. |
| Direct typed experiment `Definition -> Result` and `Result -> VerificationResult` APIs | Keep unchanged. Future SDK adapters are outward wrappers. |

### Tranche D — temporary consumed compatibility

A smaller KSD subset currently has production importers but should not be copied
upstream as-is:

- `ResultObject`, result identity, Task definition/instance identities,
  `TaskExecutionContext`, input bindings, gate records, and
  `WorkflowComposition`;
- the QE-consumed dispatch effect, authority correlation, dispatch outcome, and
  invocation-failure records; and
- generic result-codec envelope records used by KSD application composition.

Keep these temporarily while their consumers migrate. KSD's `Task` and
`Workflow` are structural `Protocol` types with live owner objects, while the
Workflow direction requires nominal runtime-enforced contracts and bounded
opaque transport. Therefore they are evidence inputs, not upstream source to
copy. The QE effect records remain temporary until the coordinated
Simulations/Workflow provider migration accepts an effect lifecycle.

### Tranche E — bounded legacy reader, only if retained data exists

Before preserving any of the following, inventory configured external stores,
archived run files, and supported consumers:

- `ksdft2effmass.workflow-run:1` aggregate bytes;
- `ksdft2effmass.sqlite.revisions` databases;
- historical claim/dispatch receipts; and
- nested-workflow or scientific-decision histories.

If real supported data exists, extract the minimum immutable decoder plus
content/integrity verification into a KSD-owned compatibility archive. Keep the
original schema and identity derivations exact. The archive may return a closed
read result or normalized export; it must not authorize new execution, repair
history, replay an external effect, or become Workflow's active store.

If no real supported data exists, test fixtures remain test artifacts and the
active reader may be deleted with the runtime that produced them.

### Tranche F — deprecate and delete rather than migrate

Subject to the retained-data and production-reference gates, the following are
candidates for deprecation and eventual deletion, not upstream translation:

| Candidate | Evidence and sequencing |
| --- | --- |
| `workflows/runs/aggregate.py`, most of `runs/records.py`, and active `runs/replay.py` | No committed production run payload/store was found. Preserve only fields required by an evidenced archive reader or temporary QE consumer, then delete the active aggregate/replayer. |
| Unused identity families in `runs/identities.py` | Retain only identities imported by production or required to decode actual retained bytes. Tests alone do not justify the rest. |
| `workflows/control/preparation.py`, `claim.py`, `reconciliation.py`, and `result_ingress.py` | No external production importer was found for the service classes. Modern Workflow must define future effect semantics; do not port these as precedent. |
| Unconsumed portions of `control/dispatch.py` and `control/authority.py` | Keep the QE-imported subset temporarily, migrate the provider path, then remove it. Do not generalize provider execution fields. |
| `workflows/persistence.py` active repository, validator, and 10.5k-line serializer | Prefer current Workflow persistence for new execution. Extract only evidence-bound legacy decoders, then delete active write/runtime behavior. |
| `ksdft2effmass.persistence` shared revision store | Used by the legacy WorkflowRun repository. Delete after any required archive reader no longer needs it; do not migrate its KSD-prefixed SQLite format into Workflow's active schema. |
| `workflows/cpn_adapter.py` | Delete after remaining legacy activation/result-mapping callers migrate. New pure owner integration uses the SDK `Firer` path and Workflow-owned selected-binding admission. |
| Private `_dft_scf_bands.py` and `_dft_scf_nscf_dos.py` probes | Retain domain topology fixtures only if still useful, then remove the legacy runtime wrappers. They do not become generic Workflow examples. |
| Nested-workflow, scientific-decision runtime, obligation, receipt, and dispatch-history machinery without a real consumer or retained history | Delete rather than making it a prerequisite for the new parent/child or effect design. |

No destructive deletion occurs until KSD records an exact reference inventory,
retained-data result, replacement route, deprecation window where applicable,
and rollback point.

## Existing upstream capability usable as-is

- The exact CPN value, definition, marking, validation, enablement, selection,
  and pure-firing kernel is usable after Tranche B establishes import identity.
- The standalone SDK's nominal `Firer`, bounded payload contracts, manifest,
  request, and closed correlated results are usable for a future KSD pure owner
  adapter. They do not replace KSD Task or effect records automatically.
- Workflow's selected-binding, source-authority, reservation, pure invocation,
  output admission, durable commit, and bounded replay services provide an
  experimental pure route. Their existing `ExperimentalWorkflowPureAction*`
  names, schemas, and identities remain unchanged until a deliberate
  compatibility migration.
- Workflow's canonical CPN definition and marking encodings are internal
  experimental execution-profile evidence. They are not retroactively KSD wire
  formats.

## First pure owner vertical slice after CPN deduplication

After Tranche B, use one structurally independent KSD pure capability to test the
existing standalone SDK rather than porting WorkflowRun. The preferred owner
shape remains the single-band Fourier-reduction calculation, followed separately
by its verifier.

The exact API stays owner-owned:

```text
SingleBandFourierReductionExperimentDefinition
    -> SingleBandFourierReductionExperimentResult

SingleBandFourierReductionExperimentResult
    -> SingleBandFourierReductionVerificationResult
```

An outward adapter may map canonical owner bytes through the SDK `Firer`. It must
preserve separate calculation and verification identities and evidence. This
slice remains blocked until an owner-authorized clean immutable experiment
revision, strict closed-schema decoders, byte-exact canonical re-encoding,
source/evidence authority, and direct-versus-adapted numerical and payload parity
exist. The current dirty experiment refactor and retained package are inventory
evidence only.

## Dependency, revision, and identity risks

1. The CPN kernel is in the full `projectkoios-workflow==0.0.0` distribution, not
   standalone SDK `0.1.0a1`. No full-runtime public release/version channel is
   accepted. KSD must use an exact reviewed source pin until distribution policy
   exists.
2. A KSD dependency change must not resolve an older published package or
   accidentally install only the standalone SDK. CI must assert the full source
   revision and imported file locations.
3. Re-exported classes have upstream Python module identities. Existing exact
   type checks work only when every old route aliases the same upstream objects;
   a partial migration would create unequal nominal classes.
4. Explicit CPN identity values intentionally retain the
   `ksdft2effmass.petrinet.colored` prefix. Renaming them would invalidate
   existing semantic identities without adding value.
5. Python pickle/module-path compatibility is unproven and excluded. If a real
   retained pickle is discovered, stop and design a bounded reader rather than
   claiming transparent re-export compatibility.
6. `ksdft2effmass.workflow-run:1`, `workflow-result:1`, QE/QoI wires, KSD SQLite
   framing, Workflow compact events, and Workflow CPN replay bundles are distinct
   schemas. Matching field names or SHA-256 algorithms do not permit identity
   substitution.
7. Legacy `TaskActivation`, operation, attempt, run, claim, dispatch, and nested
   identities must not be relabeled as Workflow occurrence, attempt, reservation,
   effect, or child-run identities. A future adapter records an explicit relation.
8. The selected-binding digest and transition-to-firer binding identity remain
   distinct. CPN enablement grants no owner invocation or calculator authority.

## Semantic parity checks

### Tranche A checks

- Verify all nine upstream production files against both the historical shadow
  manifest and the current-consumer manifest.
- Verify the exact 68-name canonical public inventory.
- Verify exact Apache-2.0 license bytes and reject owner/runtime absolute imports
  from the upstream kernel.
- Preserve the historical shadow manifest's original source revision rather than
  rewriting provenance.
- Run the 73 transformed CPN test files plus both provenance tests.

### Tranche B downstream checks

- Assert `old_root.Name is upstream_root.Name` for all 68 exports.
- Assert direct submodule object identity for every symbol imported from
  `definitions`, `enablement`, `expressions`, `firing`, `markings`, `selection`,
  `validation`, and `values`.
- Run all inherited CPN semantic tests unchanged through the old route.
- Run current campaign, workflow, persistence-reader, and QE consumers.
- Add a static check that no duplicate CPN class/function implementation remains
  under KSD after wrappers are installed.
- Verify explicit implementation identity strings, binding order, selection,
  failure classification, firing audit, and successor marking.
- Do not assert `__module__`, repr, or pickle equality.

### Later compatibility checks

- Test only supported public/domain consumers and real retained bytes.
- For an archive reader, retain exact bytes and verify decode/re-encode or closed
  incompatibility; never silently upgrade schemas.
- For the pure SDK pilot, test malformed/oversized bytes, unknown fields,
  noncanonical encoding, stale source, wrong owner correlation, exact bounds,
  direct numerical parity, payload-digest parity, and owner-independent replay.
- Exhaustive parity with unused legacy runtime internals is explicitly not a
  migration gate.

## Escalation points

Stop before choosing a convention when work would require:

- treating a KSD identity as a Workflow occurrence, attempt, effect, or child
  identity;
- interpreting legacy `indeterminate`, conflict, authorization, obligation, or
  replay outcomes as modern terminal or quiescent state;
- selecting an active writer for a KSD historical schema;
- inferring missing authority, codec, profile, or terminal evidence;
- moving calculator paths, executables, credentials, native payloads, arrays, or
  owner provider objects into Workflow state;
- defining public effect, cancellation, reconciliation, child-run, or global
  replay contracts from the KSD legacy implementation alone; or
- deleting a reader before the external retained-data inventory is complete.

## Current outcome

Review outcome: `NO_BLOCKING_FINDINGS` for Tranche A read-only parity evidence.

The lean migration does not accept the full KSD WorkflowRun/control/persistence
stack as an upstream conformance target. The next implementation is the KSD-side
Tranche B re-export and duplicate-body removal after this exact Workflow
revision is available. All later active runtime contracts require separate,
evidence-bound decisions.
