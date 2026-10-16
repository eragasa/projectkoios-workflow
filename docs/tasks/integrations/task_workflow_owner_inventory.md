# Iteration-2 owner Task and Workflow inventory

## Objective

Record the two owner shapes that must constrain any future public `Task` and
`Workflow(Task)` contracts. This inventory distinguishes owner records from
Workflow identities and execution behavior before any SDK classes are added.
It authorizes no owner mutation, calculator execution, package release, or
scientific claim.

## Evidence authority and status

### Simulations

The read-only inventory is pinned to the full immutable Simulations revision:

`c69c3fe5a949e631c6201f2f7d92297c90a5eb11`

That revision is the owner-confirmed baseline for the calculator-neutral SCF
lifecycle and the additive durable QE saved-state slice. Mutable branch names
are not evidence. The inventory does not reinterpret the historical
Simulations `task_id` as a Workflow Task, occurrence, attempt, effect, or child
run.

### `ksdft2effmass`

The `ksdft2effmass` owner reports an active, heavily dirty experiment refactor
and has not authorized a clean repository revision. Consequently, no
`ksdft2effmass` source revision is pinned and no live file is treated as
repository-level evidence.

Read-only inspection is bounded to the retained package currently located at:

`experiments/periodic-reduction/single-band-fourier-reduction/periodic1d/runs/ksdft2effmass.campaign.periodic-reduction.periodic1d.single-band-fourier-reduction.v1.run-20261014T184707Z/`

Its recorded package identity is:

`sha256:6e8d5db988df97d4b8cf7843b3baceb16e2eb70d2b03c729497a82251fca6377`

The package records `repository.git_head` as
`9a65849d886d5be499b2664e2b653c3983fab06e`, but it also records
`worktree_was_dirty: true`; that commit is therefore not a source pin for the
retained package. Its `source.sha256` content manifest names a pending
family-first layout that does not currently exist. The current dimension-last
source files inspected for this inventory match these package-retained hashes:

| Retained source | SHA-256 |
| --- | --- |
| `definition.py` | `5aa803190825a9335fcf40d484828c021d9e61a6db5a1366a05203966e647f59` |
| `experiment.py` | `f95fe4c199f283014bcb1f4e46adf3383089f09205dfa36a00b07fc9c7682648` |
| `results.py` | `d3373a47f878bc8a61f62b16433fc786aca87ebb8ef9a322d145dc51a31360a2` |
| `serialization.py` | `6a73a5ab83b0d6cd7b8856d4f3ab86c041172b6bed841fd5ce511cfeaea2cd54` |
| `verify.py` | `399b7ccb26570201a640dbd8e2bd3f33fe7866134f608bfb7dc900487cd031ee` |

This permits a provisional boundary inventory, not implementation, parity
claims, or acceptance of the pending layout. A clean immutable owner revision
remains an entry gate.

## Technical review outcome

- The Simulations owner found no blocking findings after correction against the
  pinned `c69c3fe5a949e631c6201f2f7d92297c90a5eb11` source.
- The `ksdft2effmass` owner found no blocking findings in the bounded
  provisional inventory after correction. That review accepts neither an
  implementation nor the live worktree as evidence and authorizes no mutation,
  retained-run execution, release, or scientific claim.

Neither review is an action authorization. Every implementation and adoption
entry gate below remains in force.

## Simulations inventory

### Calculator-neutral owner topology

`PwDftScfWorkflowFacade` exposes typed pending actions, correlated event
acceptance, status, and a terminal outcome without exposing the workflow
engine. `LocalPwDftScfWorkflow`, `LocalSnakesRun`, and
`build_dft_pw_scf_net()` implement the current authoritative local SNAKES
lifecycle.

The flat SCF net represents:

1. workflow start and registration action;
2. accepted task registration and submission action;
3. accepted submission and waiting;
4. calculator completion or typed failure;
5. output-analysis action;
6. analyzed output or typed analysis failure; and
7. one correlated terminal success or failure.

The transitions, actions, events, places, and lifecycle commands are not Tasks.
Registration and submission concern one correlated calculator work item
represented by owner handler-task records; they do not create independent Task
boundaries merely because each has a named action.

### Owner Task records and variation points

| Owner type | Exact retained fields or behavior | Iteration-2 classification |
| --- | --- | --- |
| `PwDftScfHandlerTask` | `evaluation_id`, `task_id`, `output_artifact_id` | Frozen/slotted owner correlation record. Its `task_id` remains an owner identifier, not a generic Workflow identity. |
| `QePwDftScfTask` | Common correlation plus `prepared_input`, ordered `pseudopotentials`, `pseudopotential_library`, absolute `executable`, `working_directory`, optional `timeout_seconds`, and explicit `execution_authorized` | QE-owned provider specialization with staging and authority semantics. |
| `VaspPwDftScfTask` | Common correlation plus one pre-staged `CalculatorExecutionRequest` | VASP-owned provider specialization with a different staging and authorization boundary. |
| `PwDftScfActionHandler` | Nominal dispatch contract for register, submit, and analyze | Execution behavior, not a retained Task definition. |
| `QePwDftScfActionHandler` | QE integration, exact QE Task tuple, QE executor, staging/execution, and QE analysis | Effectful/provider behavior; it must not enter a generic Task record. |
| `VaspPwDftScfActionHandler` | VASP integration, exact VASP Task tuple, generic calculator executor, and VASP analysis | Effectful/provider behavior with distinct failure and artifact semantics. |

Both provider handlers require unique evaluation and task identities, explicit
execution authorization, an output identifier relative to the provider
artifact root, containment within that root, and exact correlation between the
output parent and the working/execution directory. Their different resource
shapes prove that a common Workflow Task contract cannot contain a union of QE
and VASP backend fields.

The handlers emit the same neutral event vocabulary:

- `PwDftScfTaskRegistered`;
- `PwDftScfTaskSubmitted`;
- `PwDftScfTaskCompleted`;
- `PwDftScfOutputAnalyzed`; and
- `PwDftScfTaskFailed`.

These events are lifecycle evidence about owner-correlated SCF calculator work.
Caught calculator-execution and output-analysis failures are represented by
`PwDftScfTaskFailed`. Authorization denial, unknown identity, unsupported
action, and artifact-correlation violations remain raised boundary errors, not
lifecycle failure events. Neither category may be silently converted into
Workflow retries or ambiguous outcomes.

### Simulations Task candidates

The current evidence supports these boundaries without implementing them:

- **Calculator Task:** the owner-visible unit correlated by the existing SCF
  lifecycle and specialized separately by QE or VASP. Registration, submission,
  completion, failure, and analysis remain lifecycle operations around it.
- **SCF Workflow-backed Task:** when invoked by a parent, the complete
  calculator-neutral SCF Workflow would be one parent-visible Task and would
  create a distinct child SCF run. The child retains its flat local topology and
  backend-specialized calculator Task.
- **Saved-state artifact-set projection pure Task:** the implemented QE pilot is
  a cohesive effect-free operation with a strict projection-request codec,
  owner logical-identity output codec, canonical artifact-set evidence codec,
  private immutable source authority, durable evidence, and replay
  requirements. Its complete owner projection result and candidate fragment
  remain internal and are not a generic transported Task result.
- **Output analysis pure Task candidate:** provider output normalization may be
  separable when its exact immutable source and result contracts are retained.
  Existing handler analysis does not by itself establish that migration.

The additive QE pilot does not establish a VASP saved-state contract and does
not replace any SCF registration, submission, reconciliation, status, outcome,
or failure path.

### Existing child-run correlation is not a Task definition

`QeScfCandidateWorkflowCorrelation` already carries opaque Workflow-owned
identities for child export, execution plan, run, net instance, calculator
request, transition occurrence, calculator plan, effect intent, attempt,
dispatch authorization, and execution evidence. Terminal correlation separately
retains child definition, terminal occurrence, terminal place, classification,
outcome reference, and history head.

Simulations carries those identities without minting, parsing, collapsing, or
substituting them. A saved-state candidate is provider evidence, not a child
Workflow object, and possession grants no execution, staging, or scientific
authority.

## `ksdft2effmass` inventory

### Retained typed boundary

The retained experiment exposes the exact owner API:

```text
SingleBandFourierReductionExperimentDefinition
    -> SingleBandFourierReductionExperiment.execute(...)
    -> SingleBandFourierReductionExperimentResult
```

The immutable definition owns the parent toy model, plane-wave and
finite-difference inventories, parent sample coordinates, selected band,
training and disjoint evaluation samples, fitting weights, hopping ranges, and
numerical tolerances. The typed result correlates the definition with the
parent reference, both refinement studies, training and evaluation gaps, and
the complete single-band reduction result.

`SingleBandFourierReductionExperimentVerifier` provides a separate typed route:

```text
SingleBandFourierReductionExperimentResult
    -> SingleBandFourierReductionExperimentVerifier.execute(...)
    -> SingleBandFourierReductionVerificationResult
```

It reconstructs retained numerical channels without invoking the producer
Action. It is independent software verification, not an independent physical
oracle. The retained package reports bounded verification and historical parity
as passing and expressly makes no continuum-isolation, material-validation,
scientific-acceptance, or uncertainty-quantification claim.

### Cohesive Task candidates

The provisional natural boundaries are:

1. **Calculate single-band Fourier reduction — atomic pure Task.** The complete
   immutable experiment definition is the owner input and the complete typed
   experiment result is the owner output. This boundary has an independently
   reusable contract, side-effect-free numerical result, and canonical evidence
   encoders. Numerical reproducibility is qualified by owner tolerances, while
   exact replay/cache identity remains unestablished until strict decoders,
   canonical re-encoding, source authority, dependency identity, and
   payload-stability behavior are accepted.
2. **Verify single-band Fourier reduction — atomic pure Task.** The typed
   experiment result is the input and the typed verification result is the
   output. This is separately testable, has a distinct evidence purpose, and
   must not be merged with producer execution.
3. **Produce verified single-band experiment — workflow-backed Task.** A parent
   would see one experiment Task. Invoking it would create a distinct child
   Workflow run whose flat plan composes the calculate Task followed by the
   verify Task. Parent-visible terminal delivery must preserve separate exact
   references to the calculation result and the verification result and
   disposition; it must not collapse them into an undifferentiated `verified`
   identity. The verifier's `passes` value is bounded software/numerical
   reconstruction evidence, not scientific acceptance, material validation, or
   authorization.

The existing typed `Definition -> Result` and `Result -> VerificationResult`
APIs remain unchanged. An outward owner adapter may invoke them; reusable
numerical modules do not import Workflow service, compiler, persistence, or CPN
runtime implementations.

The following remain ordinary owner implementation, not Tasks:

- coordinate conversion and selected-band slicing;
- individual diagonalizations;
- each cutoff, grid point count, hopping range, Fourier coefficient, or matrix
  operation;
- result serialization helpers;
- report and figure rendering; and
- individual structural or numerical checks inside the verifier.

Those operations currently lack an independent authority, failure, replay,
scheduling, or reusable contract boundary sufficient to justify durable Task
identity. Parameterization and loop fan-out alone are insufficient.

### Owner-controlled payloads

The definition and result contain models, quantities, arrays, spectra, matrices,
range studies, and tolerances. Canonical input, result, and verification bytes
are owner documents. Their bodies and native numerical objects remain in an
owner-controlled source/evidence repository.

Workflow may retain bounded opaque source references, owner logical result
identities, schema/codec descriptors, exact payload SHA-256 values, invocation
and occurrence identities, and compact replay correlations. Payload SHA-256
identifies exact canonical transport bytes; it is not the experiment's semantic
identity. Workflow compact state must not retain the numerical document bodies.

The current serializers are evidence encoders. The pilot still needs strict
owner decoders that reconstruct exact typed values, reject unknown fields and
invalid bounds, and require byte-exact canonical re-encoding before those
formats can serve as SDK request and result codecs.

## Common identity model

The two owners require the following domains to remain distinct:

| Identity domain | Meaning |
| --- | --- |
| Task definition | Reusable immutable owner operation contract. |
| Task instance | One Task configured in a containing Workflow definition or plan. |
| Parent Workflow run | Durable execution of the containing flat plan. |
| Task invocation | One parent request to execute one Task instance. |
| Transition occurrence | Exact selected CPN occurrence that makes execution eligible. |
| Attempt | One execution attempt under the route-specific authority. |
| Owner result | Owner semantic output identity. |
| Payload SHA-256 | Integrity identity of exact canonical transport bytes. |
| Child Workflow definition and plan | Separately compiled closure backing a workflow-backed Task. |
| Child Workflow run and net instance | Distinct durable execution created for one parent invocation. |
| Child terminal delivery | Correlated delivery from exact retained child terminal evidence to the parent. |

No owner `task_id`, evaluation identity, run directory, evidence-package
identity, SDK payload digest, occurrence identity, or child-run identity may be
substituted for another domain by matching strings.

## Execution-route separation

- The QE saved-state projection and proposed `ksdft2effmass` calculate and verify
  Tasks use the pure route only after exact owner codecs and source authority are
  accepted.
- SCF registration, calculator submission, cancellation, reconciliation, and
  ambiguous process outcomes are effectful and remain outside `Firer`.
- A workflow-backed Task uses a child-run service, not a pure firer and not an
  embedded child CPN.
- Handlers, firers, executors, repositories, and child-run services execute
  retained definitions; none is itself a Task definition.

## Minimum cross-owner changes still required

This inventory constrains future work but does not accept exact APIs.

### SDK

- Add no `Task` or `Workflow` classes to `0.1.0a1`.
- After the two-owner gate, define nominal immutable Task source and
  `Workflow(Task)` composite contracts without owner-domain fields.
- Preserve `Firer` as the non-overridable pure execution template and keep
  effect handlers and child-run services separate.
- Represent only bounded opaque owner identities, source/payload descriptors,
  and composition references; exclude callables, providers, paths,
  executables, credentials, repositories, and numerical objects.

### Compilation and bindings

- Retain one execution route per Task instance: pure atomic, effectful, or
  workflow-backed.
- Bind pure Tasks to an exact owner integration manifest and authoritative source
  mapping.
- Bind workflow-backed Tasks to a separately compiled child definition and plan;
  do not copy child topology into the parent CPN.
- Reject direct and indirect definition cycles and backend substitution.

### Runtime

- Encapsulate the existing durable pure-action chain as pure Task execution only
  through an explicit compatibility migration.
- Create exactly one correlated child run per accepted workflow-backed Task
  invocation, with explicit idempotence and restart behavior.
- Admit parent delivery only from the exact retained child terminal result and
  correlation chain.
- Define closed outcomes for child start uncertainty, child terminal conflict,
  cancellation, and parent/child recovery before effectful adoption.

### Persistence and replay

- Persist compact parent Task invocation and child-run correlation identities in
  the same accepted atomic boundary as their lifecycle advancement.
- Retain child definition/plan/run/net and terminal-delivery evidence without
  owner payload bodies.
- Reconstruct parent/child state without owner reinvocation and without
  fabricating missing legacy links.
- Keep source bodies, numerical arrays, native artifacts, provider resources,
  executables, paths, and credentials outside Workflow persistence.

### Owner adapters

- Keep direct typed owner APIs authoritative.
- For each adopted Task, retain or add its owner-approved strict request,
  output, and evidence codecs plus immutable source retention. Preserve the
  completed QE saved-state request / logical-identity output / artifact-set
  evidence codec split; `ksdft2effmass` still requires strict decoders and
  canonical re-encoding.
- Demonstrate owner-declared numerical parity between direct and
  Workflow-backed execution within the declared tolerances. Exact
  payload-digest equality must be demonstrated separately and must not be
  assumed.
- Retain negative malformed-payload, stale-source, wrong-correlation,
  wrong-backend, bound, replay, and owner-non-reinvocation evidence.

## Findings and gates

The shared invariant is intentionally small: a parent sees an immutable Task
instance through bounded opaque owner contracts, while retained execution
behavior is selected separately. Simulations demonstrates provider
specialization and its existing local owner action/event lifecycle, plus one
bounded durable pure-action slice; it does not yet prove Workflow effect
lifecycle. `ksdft2effmass` provisionally demonstrates typed pure calculation,
independent verification, and natural pure composition. Neither justifies
putting owner resources or scientific fields in the generic SDK.

The next implementation gate remains closed until:

- the `ksdft2effmass` owner supplies and authorizes one clean immutable source
  revision;
- the proposed calculate and verify boundaries are reviewed against that exact
  revision;
- strict bidirectional owner codecs and immutable source retention exist;
- direct-versus-adapted parity is demonstrated;
- one workflow-backed Task proves distinct parent invocation, child plan, child
  run, terminal delivery, and replay identities; and
- both owners accept the resulting common invariants.
