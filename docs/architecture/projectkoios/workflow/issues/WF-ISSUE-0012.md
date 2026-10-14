# WF-ISSUE-0012 — External-occurrence reservation representation

- **Kind:** architecture
- **Status:** NARROWED
- **Workflow-local scope:** CPN markings, reservations, ambiguity, refinement, and firing audit
- **Authoritative owner:** Workflow CPN/runtime architecture

## Problem or question

How should an effect-bound logical transition reserve exact source tokens, expose operational lifecycle state, preserve source CPN behavior during a long-running effect, and admit successful outputs without creating a hidden second scheduler?

The question is not whether provider execution occurs inside a CPN firing: it does not. Every candidate dispatches outside database transactions and admits provider evidence before a success-only domain commit. Failed, rejected, cancelled, lost, or indeterminate attempts never pretend that the reserved logical/domain transition fired.

## Current evidence

The live CPN evidence supports pure selected firing with explicit external-output binding. `ksdft2effmass` control evidence reserves exact work before dispatch and treats post-entry uncertainty as indeterminate. Simulations review recommends a lifecycle subnet whose begin transition makes ownership and duplicate-launch prevention visible in a marking. Operator direction requires lifecycle, retry, cancellation, ambiguity, and child correlation to remain explicit CPN semantics rather than a hidden DAG/task engine.

The two-marking possibility is also valid: one immutable domain CPN marking may remain unchanged while a correlated authoritative operational companion CPN holds reservations, attempts, ambiguity, and cancellation tokens. “CPN is authoritative” therefore does not require operational tokens to be inserted into domain places.

The candidates share these identities:

```text
D   exact compiled definition
N   net-instance identity
M0  enabling source/domain marking revision
T   source logical/domain transition
b   selected ordered binding over exact token occurrences
O   one occurrence identity for (D, N, T, M0, b)
Ai  attempt i under O
```

A later loop that enables `T` again creates another occurrence. A permitted operational retry creates another attempt under `O`. Operation-scoped start, observation, reconciliation, and cancellation keys derive from `O` and `Ai`, never from a display task name.

## Authority dependency

This packet depends on [`WF-ISSUE-0002`](WF-ISSUE-0002.md) but does not decide grant issuance or revocation. Begin/reservation records work ownership only; it never grants effect authority. Exact denial, expiry, or observed revocation before `start` routes through an explicit pre-effect policy transition. Revocation after possible start cannot imply non-execution, automatic restoration, or permission to relaunch; the occurrence remains subject to observation or reconciliation under its retained start identity.

## Consequence

The choice changes marking meaning, compiler expansion, concurrency control, selection and priority preservation, replay reconstruction, visualization, persistence schema, output-capacity handling, and migration equivalence. Choosing without a refinement model risks either a hidden state machine beside the CPN or an expanded lifecycle net that exhibits domain-visible traces unavailable in the source net.

An irreversible effect can also finish when its intended output place has become full or an output identity now conflicts. Any viable design must prevent a successful provider effect from being discarded or misreported merely because domain admission is temporarily or permanently blocked.

## Candidate A — predecessor marking plus reservation ledger

One Workflow transaction validates `(D, N, M0, T, b)`, stores `O`, and reserves every consumed token occurrence. `M0` remains the domain marking while the scheduler excludes conflicting bindings through a durable reservation ledger. On admitted success, the engine revalidates the predecessor and performs the original pure firing with the external-output binding.

This candidate minimizes compiler expansion and resembles the current pure-firer contract. Its principal weakness is semantic work ownership outside a CPN marking. It must define durable predicate protection for `READ`, `INHIBIT`, source priorities, and output capacity. Merely reserving consumed tokens is insufficient because another firing could change a read value, insert a token into an inhibited place, or fill a bounded output place after an irreversible effect starts. Long-lived database locks are not acceptable.

A database table may index authoritative CPN state, but it must not become an undocumented second process formalism. Candidate A remains viable only if reservation and predicate semantics are explicit, replayable, and equivalent to a declared operational model.

## Candidate A-prime — correlated companion operational CPN

The source/domain marking remains `M0`. A distinct, generated operational CPN marking contains an occurrence token that references `D`, `N`, `M0`, `T`, `b`, exact token occurrences, predicates, capacity claims, and attempts. Domain enablement consults the correlated operational reservation semantics so conflicting source bindings cannot start.

Prepare, stage, authorization, dispatch, ambiguity, observation, reconciliation, cancellation, collection, and retry are transitions in the operational companion CPN. Admitted success enables one engine-controlled domain commit against the exact source transition. Domain and operational histories are both authoritative and correlated, while their place/color namespaces remain separate.

This candidate avoids placing lifecycle tokens in scientific/domain places and gives reservations a CPN representation. Its risks are cross-net atomicity, a more complex enablement contract, and accidental emergence of two independent schedulers. Compilation and persistence must prove that the companion cannot advance in a way inconsistent with the source reservation.

## Candidate B-prime — generated escrow/refinement subnet

The compiler expands an effect-bound source transition into a versioned operational fragment within one flat executable CPN. An atomic pure `begin_occurrence` firing validates `b`, escrows exact `CONSUME` token occurrences, captures bound `READ` values and inhibitor-absence evidence, reserves known output identities/capacity where possible, and emits an occurrence token for `O`. Provider effects happen outside the kernel. A later `commit_occurrence_success` firing consumes admitted terminal evidence and emits the source transition's domain outputs exactly once.

### Source-marking projection

This candidate requires an explicit projection `π` from every expanded marking to source-level state and reservation evidence:

- Before begin, `π` is the original source marking with no occurrence reservation.
- During the lifecycle, escrowed token occurrences project to their original source places as occupied-but-reserved. They are unavailable to competing `CONSUME` bindings, continue to satisfy or block source-place occupancy where required, and count against source capacity according to the declared refinement rule.
- Operational-only transitions are stuttering steps under the source trace: they change lifecycle evidence but do not claim that `T` fired.
- Successful commit is the single projected source transition firing.
- Failure, rejection, cancellation, loss, ambiguity, retry, restoration, and compensation do not project as `T`.

Generated occupancy-shadow records may protect source inhibitor and capacity semantics, but they are operational references to escrowed occurrences—not cloned domain tokens. The compiler must prove that generated operational transitions cannot enable a new domain behavior that the selected source transition and declared concurrency policy did not permit.

### Token custody and restoration

Each consumed token occurrence exists in exactly one custody location. Begin moves the original occurrence into an escrow record containing original place, color, value, token identity, binding role, and provenance. An occupancy shadow has a distinct operational identity and only references the escrowed occurrence.

Any pre-effect abort or policy-authorized restoration is a visible pure transition that returns the same original occurrence identity to its declared source place and records the custody move. Compensation creates a new identified result with explicit provenance; it is not restoration. Post-effect ambiguity never restores inputs automatically.

This candidate keeps operational ownership visible in the compiled marking and naturally exposes ambiguity and cancellation to visualization. Its costs are a larger net, a formal refinement proof, a source-to-expanded-transition map, and exact escrow/capacity semantics.

## Candidate C — author-visible lifecycle fragment

Instead of presenting one atomic source transition and asking the compiler to infer an equivalent split, workflow authors explicitly compose a standard reusable lifecycle fragment through typed ports. The domain definition therefore states request preparation, occurrence begin, success admission, failure evidence, and any restoration or compensation routes.

Compiler sugar may instantiate the same accepted fragment, but the source contract no longer pretends that begin/commit are automatically equivalent to an atomic transition. This is clearest when external work has scientifically meaningful intermediate states or when result admission can wait for capacity.

Its cost is a more verbose authoring surface and possible repetition unless base templates and validating subclasses remain strong. It may be preferable as the normative semantics even if a concise source-language helper generates it.

## Candidate D — native split-occurrence kernel extension

The kernel could gain a native long-running occurrence primitive distinct from ordinary CPN firing. This may simplify compilation but expands the trusted kernel with effect-lifecycle concepts and risks making CPN firing no longer the sole process semantic.

This candidate is retained for comparison but is currently disfavored. It should be rejected unless compiler-expanded or companion CPN alternatives cannot preserve required semantics without greater complexity.

## READ and INHIBIT semantic choice

Snapshot-at-begin and validity-until-commit are both defensible and scientifically observable:

- **Snapshot at begin:** begin captures exact bound `READ` values and inhibitor absence. Later changes do not revoke an already admitted occurrence. This can be linearized as selecting the effect before later independent firings.
- **Validity until commit:** relevant read values and inhibitor predicates must remain valid until domain commit. This requires durable read/predicate reservations or a defined invalidation route before irreversible launch.

The current recommendation is that an effect fragment must declare its rule explicitly; external execution must not imply snapshot semantics automatically. A global default, if adopted, must still be encoded in the compiled plan and visible in provenance.

## Output capacity and result buffering

Every candidate must address output multiplicity, capacity, identity collision, and output-expression failure:

1. If output identities and maximum multiplicity are known at begin, the occurrence may reserve exact capacity and identities.
2. If they depend on external evidence, successful mechanical output enters a durable result buffer. A later guarded domain-admission transition waits for capacity and validates normalization, identities, expressions, and output colors.
3. A normalization or admission failure retains the mechanical result and evidence in an explicit terminal/blocked operational state. It does not discard output or fire the source transition.
4. Capacity reservation and escrow must not free source capacity early in a way that enables traces forbidden by the source/refinement contract.

Result buffering may cause a completed effect to wait indefinitely for domain admission; that state must be visible, cancellable only under defined semantics, and handled by explicit operator or domain policy rather than relabeled as provider failure.

## Fixed scenario traces

| Scenario | A: ledger | A′: companion CPN | B′/C: escrow lifecycle | Required invariant |
|---|---|---|---|---|
| Successful effect | Reserve; run; CAS original firing | Operational begin/run; domain commit | Fire begin; run; fire success commit | Domain outputs exactly once |
| Pre-effect rejection | Explicit release policy | Rejected token and release transition | Rejected evidence; retry or explicit restore | No hidden restoration or domain firing |
| Stage wrote state then failed | Retain effectful failure and reservation | Stage-effect token routes to reconcile/terminal | Escrow retained; no pre-effect restore path | Write is not misclassified as rejection |
| Crash after staging | Reservation and receipt survive | Companion staged marking survives | Occurrence/staged tokens survive | No second workspace/effect |
| Lost start acknowledgement | Ambiguous attempt under reservation | `DispatchAmbiguous` token | `DispatchAmbiguous` token | Reconcile same start key only |
| Reconcile never-started | Guarded new attempt under `O` | Retry transition under `O` | Retry transition under `O` | Explicit policy and attempt identity |
| Reconcile started | Observe original handle | Move to running with original handle | Move to running with original handle | Never relaunch |
| Cancellation races success | Deterministic occurrence projection | Guarded companion terminal projection | Guarded lifecycle terminal projection | One terminal view; prior success remains success |
| Lease expires | Retain reservation; observe/reconcile | Lease token expires; effect state unchanged | Lease token expires; escrow remains | Expiry is not non-execution evidence |
| Eligible retry | New `Ai` under `O` | Retry transition creates `Ai` | Retry transition creates `Ai` | Retry is not a new occurrence |
| Loop re-enables `T` | New reservation and `O` | New correlated occurrence | New begin and `O` | Loop activation is not retry |
| Concurrent same-`T` bindings | Exact overlapping reservations conflict | Companion reservations conflict by token identity | Begin firings conflict on escrowed occurrences | Disjoint bindings may proceed |
| Overlapping `READ` | Snapshot or predicate reservation | Declared companion policy | Declared fragment policy | Exact admitted read semantics |
| Concurrent inhibitor insertion | Predicate reservation or snapshot rule | Occupancy/predicate token | Projection/occupancy shadow | No post-effect surprise |
| Bounded output becomes full | Capacity reservation or result buffer | Companion capacity claim/buffer | Capacity token or result buffer | Successful effect remains retained |
| Output identity collision | Reserved identity or blocked admission | Explicit collision evidence | Explicit collision evidence | No overwrite or fabricated output |
| Normalization fails after exit 0 | Durable mechanical result buffer | Terminal mechanical token, failed normalization transition | Same | Mechanical success remains evidence |
| Child launch acknowledgement lost | Correlated nested reservation | Child operational ambiguity token | Child lifecycle ambiguity token | No duplicate child net instance |
| Replay after restart | Rebuild domain plus ledger | Rebuild both markings | Rebuild expanded marking | No provider call before ready |

## Evaluation criteria

1. **Authoritative semantic ownership:** all work ownership is visible in authoritative domain and/or operational CPN markings; database indexes remain projections.
2. **Formal refinement:** every operational state maps to a defined source marking/reservation state, and operational stuttering cannot invent domain traces.
3. **Selection and priority:** generated begin transitions preserve source transition priority, conflict, and directed-selection evidence.
4. **Concurrency correctness:** multiple enabled bindings, overlapping reads, disjoint consumes, inhibitors, and capacities remain well-defined.
5. **Token custody:** domain occurrences are never cloned, silently dropped, or silently restored.
6. **Output admission:** capacity, multiplicity, identity, normalization, and expression failures preserve successful effect evidence.
7. **Crash recovery:** domain and operational state reconstruct before scheduler or worker readiness.
8. **Ambiguity safety:** ambiguous or lost states enable reconciliation only, never automatic restore or relaunch.
9. **Observation monotonicity:** repeated or reordered provider observations remain evidence but cannot regress the marking.
10. **Cancellation determinism:** cancellation/success races produce one deterministic terminal projection.
11. **Provenance and archival:** consumed, read, inhibited, escrowed, staged, authorized, observed, restored, compensated, and produced evidence remain reconstructable; garbage collection cannot remove required evidence.
12. **Compiler complexity:** expansion, namespacing, source mapping, and visualization remain deterministic and explainable.
13. **Migration equivalence:** current CPN, `ksdft2effmass`, Simulations, Ingestion, References, Applications, and child-net fixtures remain representable.

## Alternatives and recommendation

No candidate is selected. The prior lean toward a simple Candidate B is withdrawn until refinement, capacity, and custody semantics are proven.

Current evidence favors comparing A-prime and B-prime/C most closely:

- A-prime keeps domain and operational markings cleanly separated but requires cross-net atomicity and one coordinated scheduler semantics.
- B-prime makes escrow and lifecycle visible in one flat net but requires occupancy shadows and a formal projection to prevent domain-trace changes.
- C may be the clearest source-language contract even if it lowers to B-prime, because authors explicitly choose lifecycle and snapshot semantics.

Candidate A must not remain an opaque ledger. Candidate D should remain a last resort rather than expanding the trusted kernel prematurely.

## Resolution gate

An implementation-independent model and independent review must establish:

- atomic begin validation of marking revision, selected binding, exact token occurrences, predicates, capacity claims, and unique occurrence/start keys;
- selection/priority preservation under source-to-lifecycle lowering;
- formal source-marking projection and operational stuttering/refinement;
- exact custody, restoration, compensation, and output-buffer identities;
- no duplicate launch and ambiguity-to-reconcile-only behavior;
- explicit distinction between pre-effect rejection and effectful staging failure;
- success-only domain firing and separate guarded domain failure routes;
- monotonic observation admission and deterministic cancellation races;
- result-normalization failure after mechanical success;
- child launch, terminal observation, and cancellation under the same occurrence rules;
- replay of domain and operational markings before scheduling, with no provider call; and
- archival retention sufficient to reconstruct projected source state.

The decision record must state the chosen READ/INHIBIT semantic rule, capacity strategy, rejected alternatives, and evidence for representative owner workflows. It must not select an implementation package sequence.

## Affected architecture

CPN source language, compiler, composition, kernel integration, runtime, persistence, lifecycle fragments, service transactions, worker protocol, child-net correlation, provenance, archival, visualization, and migration equivalence.
