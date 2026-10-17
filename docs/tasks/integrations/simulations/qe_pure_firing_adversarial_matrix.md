# QE pure-firing adversarial coverage matrix

## Objective

Inventory the exact positive and negative evidence for the bounded QE saved-state
pure-firing path before adding more runtime infrastructure. The matrix identifies
real seam gaps without treating repeated tests as new safety properties.

This is evidence for one Simulations-owned pure action. It does not establish a
public Task or Workflow API, complete execution-plan or behavior-profile
closure, an OS-process sandbox, effectful execution, global scheduler replay,
full CPN-bindings conformance, production release readiness, or second-owner
generality.

## Evidence baseline

- Workflow rollback baseline:
  `projectkoios-workflow@ee581b5c148adb0c678046ecfb50de0fad72da30`.
- Standalone SDK source used by owner CI:
  `projectkoios-workflow@fe600fa1b857cd030832b226a8e21e0a30f4f1b6/sdk`,
  version `projectkoios-workflow-sdk==0.1.0a1`.
- Simulations published validation baseline:
  `projectkoios-simulations@4f05789d63f4cb2851c1e4f0ee0d6666e1875a67`.
- Simulations production-source baseline:
  `projectkoios-simulations@c69c3fe5a949e631c6201f2f7d92297c90a5eb11`.

The matrix uses the production slice at `c69c3fe` and its test, provenance, and
CI descendants through `4f05789`. The final descendant is test-only: it extends
the real-owner vertical test with exact intermediate-identity assertions,
repository reopen, and post-replay privacy scans without changing production
source. Pull-request CI run
[38996011590](https://github.com/eragasa/projectkoios-simulations/actions/runs/38996011590)
passed at that exact head. A separately composed environment with the optional
full Workflow runtime passed the updated cross-repository test (`2 passed`) and
complete Simulations suite (`698 passed, 7 skipped, 202 subtests passed`).

## Exact boundary chain

The current route crosses these records in order:

```text
ExperimentalWorkflowSelectedBindingEvidence
→ ExperimentalWorkflowPureActionInputBindings + opaque source reference
→ ExperimentalWorkflowPureActionAuthorizedInputs
→ ExperimentalWorkflowPureActionReservationResult
→ ExperimentalWorkflowPureActionInvocationOutcome
→ ExperimentalWorkflowMappedActionResult
→ ExperimentalWorkflowPureActionFiringOutcome
→ ExperimentalWorkflowPureActionCommitResult
→ compact / CPN / lifecycle / safety replay results
```

No record in that chain grants calculator authority. The owner request and
artifact-set evidence bodies remain outside compact Workflow persistence.

## Identity and seam matrix

| Boundary | Exact retained or asserted evidence | Principal adversarial evidence | Assessment |
| --- | --- | --- | --- |
| CPN enablement and deterministic selection | Selected-binding evidence `3ca155cd09bf8fb0cd921688a894284665bbad7f284df3c1f3bd668644765bd4`; representation profile `projectkoios.workflow.experimental-selected-binding-canonical-json:1` | `test__ExperimentalWorkflowFiringRequestFactory.py` rejects nonselected bindings, changed enablement, changed ordering, wrong definition, wrong predecessor, role/codec/bound substitution, and oversized values. | Covered for the bounded shadow-CPN route. The umbrella CPN-bindings contract remains proposed. |
| Pure-action plan and deployment linking | Output mapping `7a1664a7de8770bc9e068bf09f8e62793c57f5eef5bf4c34c5faf3e331afbd3e`; execution plan `a0f9aa9d5abd12da4e5099cc60c9f26063505cdd988d00898c3b8f1250a98271`; manifest `140197dc0fd386c7c9e433f3ff47c609d5b9ddfef4dd3b3620cecf1d73bf8644`; execution bindings `a54ebcbbf88998d7fd3215bc00a13c885f514790febcab40364e3b1aea02126f`; input mapping `0f7d665bb1b2d186c383569e80c4286b65690f92bd69bfa94b31cf66c4348620`; input plan `efa293c0c860486bc5f1b4741b69beb1181c2509025f8c77aae02dfead770361`; input bindings `ca98772a5cce04065134cdb4d3d57a39712c0c655aab0076b0d75812ca7493e5` | `test__ExperimentalWorkflowPureActionExecutionPlan.py` rejects changed mapping, missing or changed firers, and nested-record forgery; changed distribution or selected-binding-profile identity produces different bindings. Input tests reject changed source mappings and profile substitution. | The exact candidate identities are closed and the reservation lifecycle retains plan and execution-binding identities. Complete authoritative plan and deployment bindings remain open. |
| CPN definition and execution profile | Definition representation profile `projectkoios.workflow.experimental-cpn-definition-json:0`; candidate CPN execution profile `3321f8a87314f964af4a8fb1c8cc732e80c2b7686f1f2fbe68329d708d931173`; CPN plan `3ba808794b16953f3fceb20b9f18b204912582ea6dbe3d36100bf321b81b3411` | CPN representation tests reject unknown fields, noncanonical values, changed closed state, and byte-unequal re-encoding. CPN replay tests reject execution-profile substitution and unsupported profiles. | Covered for exact CPN transcript refiring. The selected-binding adapter profile is still correlated transitively rather than reconstructed as a complete durable global profile. |
| Owner source resolution and input admission | Opaque source-reference identity `03eb0408eb031e2e951b79a265048219d2c3800b3556576026e441341e75ae39`; SDK request `417d0d912f96acac7a65ff5d42cc85de670d304805a50b859a01123d2162a64d`; authorized inputs `a69fcf048f90500b0b35ea7153ccd8e15a1b7553ffd36a9aab0e2d53acb09b3d` | Input-authority tests cover absent, incompatible, corrupt, exception, missing, duplicate, reordered, wrong-contract, path-shaped, and forged sources. Reservation and invocation tests mutate the source before request exposure, during owner invocation, before firing, and immediately before commit. | Covered for the owner-controlled content-addressed adapter candidate. Production retention authority remains an owner/deployment decision. |
| Reservation and predecessor authority | Reservation `38596e52afac8f80438b5e26fdf506f3d41dc4a500a3d40ec8b8be05377fddb6` binds plan, deployment, selection, request, source, occurrence, attempt, marking, and revision identities. | Reservation tests cover stale predecessor, changed source, forged identity, attempted rewind, consumption, and concurrent attempts. Invocation revalidates after live-worker resolution and after owner return. | Covered for one occurrence and attempt. It is not global scheduler-state replay. |
| Live integration admission and owner invocation | Manifest identity above; invocation outcome `b8cf4187884dc9e087ea4de9760e51fd016378cfba7d29ce6f62df275ac7dc52` | Worker validation rejects manifest and descriptor mismatch, duplicate firers, and non-Firer objects. Invocation tests cover worker mismatch, request mutation, owner exception, closed rejection/failure, stale state, stale source, and unmappable success. Simulations tests reject malformed owner requests, overbound evidence, mismatched reconstruction, and a syntactically valid but semantically wrong owner identity. | Covered in-process. Malformed process frames, timeout, signal exit, and process containment are intentionally unavailable until a separately accepted OS-process probe. |
| Output and evidence admission | Exact `artifact_set_identity` output contract, exact ordered `artifact_set` evidence contract, and mapped external variable | SDK `Firer.fire()` requires every output contract and rejects unregistered, reordered, wrong-metadata, overbound, or over-total-bound payloads. The mapper independently rejects missing evidence, reordered evidence, wrong role/codec metadata, digest substitution, malformed ASCII, path-shaped identity text, stale correlation, and unregistered CPN variables. | Missing, extra, swapped, and substituted roles are already rejected at SDK and mapping seams. Workflow deliberately does not parse the opaque owner evidence document. |
| Pure CPN firing | Firing outcome `4fb981884ffee5577ab25cec6e0a940a1137a8a6a99f6707a06fdef6e81288b5`; CPN firing result `fa47c1246ee164eab15723cd8fe9ff8ac556259e5939d4db630135911d111ccf`; successor marking `70ae79097bc2005a6992057373fbbcc7540b1167f7485d7d29c12945cdb45fb6` | Firing tests reject definition substitution, invalid output color, stale reservation, changed source, and stale commit after a valid candidate. | Covered for one exact flat CPN occurrence. |
| Atomic durable commit | Compact commit `5c58d4827f77d95a01d52484fc4ac628a385d9984ae8e1adc3db1ea684248df4`; compact event SHA-256 `f6968d85a163d28563de41a287f37f91a489a88e7bf8f65307d098c68aa1a61a` | Durable tests cover precommit rollback, process crash, stale source, stale predecessor, repository mismatch, exact idempotence, conflicting commits, corruption, migration rollback, and concurrency. The architecture test prohibits production execution modules from calling the compact-only writer. | Covered for the canonical experimental durable writer. No additional persistence variant is justified. |
| Lifecycle and owner-independent replay | Reserved event `2f59dd5b34f32717b6928f27be19b449ede6d9ee2d4418b2daa0bc3e7bdced54`; committed event `a8fef9583c9dd56558099b8d1e1209164ce04544909ccfe9e2d2a28bcd39a103`; compact, CPN, lifecycle, and safety replay | Replay tests cover absent legacy evidence, unsupported versions, corrupted bundles, changed result/output/successor state, profile substitution, migration rollback, and partial histories. The real-owner test removes the owner source and proves one owner call. | Covered as four bounded replay views, not complete runtime replay. |
| Durable privacy after reopen and replay | SQLite stores compact identities, source-authority references, lifecycle events, and content-addressed CPN bundles, but not owner request/evidence bodies | Existing SQLite tests inspect compact schemas. Simulations test-only commit `4f05789d63f4cb2851c1e4f0ee0d6666e1875a67` reopens the repository, performs every replay from the reopened instance, and scans again for exact owner request bytes, artifact-set evidence bytes, the private source root, and every owner retention reference. | The gap closure is immutable test evidence. It proves exact-byte and current-schema absence, not confidentiality under arbitrary alternate encoding. |

## Coverage findings

### No duplicate infrastructure required

The audit found no reason to add another repository, replay service, event
variant, or admission record. Existing tests already cover the proposed
missing/extra/swapped payload roles, semantically wrong owner identity,
manifest mismatch, distribution-linked binding change, and source mutation
seams.

### Bounded gaps that remain open

- **Selected-binding adapter-profile reconstruction:** the current identities
  transitively bind the selected-binding profile, but compact/lifecycle replay
  does not independently reconstruct a complete authoritative adapter profile.
  Revisit only for the minimum QE supported-profile closure or after
  second-owner evidence.
- **OS-process framing and containment:** no process protocol exists, so the
  current suite cannot claim rejection of truncated process frames, child
  timeout, signal exit, environment leakage, or orphaned process trees. Revisit
  only after package/profile identity and worker security bounds are selected.
- **Production source authority:** the adapter proves content-addressed immutable
  reads, not who operates durable production retention or may issue references.
  That remains an owner/deployment policy decision.

These gaps do not invalidate the stated bounded in-process QE evidence. They do
block claims of supported deployment, worker isolation, or complete
plan/profile closure.

## Current review classification

- Finding disposition: `SAFE_TO_DEFER` for each bounded gap above.
- Review outcome: `NO_BLOCKING_FINDINGS` for the existing bounded QE pure-firing
  evidence, including test-only commit `4f05789d63f4cb2851c1e4f0ee0d6666e1875a67`.
- Operator request: `NONE` for matrix construction and local adversarial
  validation. Commit, push, release, merge, process execution policy, and
  production source authority remain separately controlled operations or
  decisions.
