# Experimental pure-action CPN firing evidence

## Scope

This record covers the bounded v0 Workflow-owned step from one mapped, current
owner invocation outcome through the provenance-bound pure CPN firer. It
computes a candidate successor and audit only. It does not consume the
reservation, persist the result, or authorize a commit.

## Implemented boundary

- `projectkoios.workflow.execution.ExperimentalWorkflowPureActionFiringService`
  reconstructs and correlates the authorized inputs, successful CPN-plan-bound
  reservation, mapped invocation outcome, exact selected-binding evidence,
  retained canonical flat-definition bytes, supplied flat CPN definition, and
  supplied predecessor marking.
- Definition, marking, transition, selection, reservation, request, plan mapping,
  and invocation identities must agree before CPN firing.
- The service reloads every authoritative input source and revalidates the exact
  predecessor immediately before constructing `ColoredPetriNetFiringInput`.
- `ColoredPetriNetTransitionFirer` replays definition validation, marking
  validation, enablement, selection, directive correlation, external-output
  assignment validation, occurrence reconstruction, output evaluation, output
  color validation, and successor derivation.
- Workflow preserves a structured CPN rejection without a successor, contains
  an unexpected firing exception, and repeats source and predecessor
  revalidation after pure computation.
- A post-computation stale result preserves the pure firing evidence but cannot
  be treated as a commit candidate.
- Direct construction of an outcome replays the pure firing input and requires
  exact equality with the supplied CPN result.

All records remain experimental v0 prerelease records.

## Adversarial evidence

Focused tests cover a valid mapped string output producing the expected
successor token, output-color incompatibility producing a closed CPN rejection,
stale predecessor rejection before firing, a source change after pure
computation preserving the candidate while blocking commit, and post-reservation
definition-plan substitution.

Validation from the uncommitted candidate on base Workflow revision `d4a8f11`:

- focused authority/admission/reservation/invocation/plan/firing tests:
  `42 passed`;
- full Workflow suite: `362 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `50` source files;
- Ruff, formatting of changed sources, architecture, runtime dependency,
  shadow-provenance, documentation-link, and diff checks: passed;
- pure-firing source SHA-256:
  `5f9236811563e301fe8af4318db286b41eb6fdd123446050b437faff6dbb822f`;
- focused test source SHA-256:
  `f2a21c9f935936f2b5c7a98e0cab9735c4bc0f04b84ae5be76b7b999fc5260a5`;
- two Workflow wheels built with `SOURCE_DATE_EPOCH=315532800` were
  byte-identical, SHA-256
  `c3b40d3e980a2a2f5123806439ecd6113e500f639a78520499e5bc5832b4d810`;
- the unchanged standalone SDK suite and wheel boundary remain unaffected.

Deterministic successful fixture identities:

- mapped invocation outcome:
  `11abed96ae17d3201e58ff152b3075e297456ed710bc99314d9c5afa7faa7560`;
- pure CPN firing result:
  `7b2fc736bc9a1061ff3be890f4692c62960a2b8e4def40e3bb3c2cbb5fee818f`;
- candidate successor marking:
  `e01c016b26b52d70afbc7c7a481ed591e221f924ea45298243e3fc130f9ecf5f`;
- pure-action firing outcome:
  `83f48104089bcda48cbd5a2b80509da4a3897048b36009ed8340f0ff9ff9a59e`.

## Remaining gaps

The bounded [CPN plan candidate](pure_action_cpn_plan_evidence.md) now binds
canonical flat-definition bytes and a candidate execution profile, but it does
not close every field of the proposed complete `WorkflowCpnExecutionProfile` or
`WorkflowExecutionPlan`. The supplied definition is verified byte-for-byte
against that plan; the predecessor marking remains a correlated runtime
argument. This service is software evidence for the pure firing seam, not
complete `WorkflowExecutionPlan`, `WorkflowExecutionBindings`, or
`projectkoios.workflow.cpn-bindings` conformance.

The firing candidate does not itself claim invocation, consume a reservation,
or advance the authoritative marking. The later
[atomic-commit candidate](pure_action_atomic_commit_evidence.md) consumes and
advances compact in-memory state under one lock, but durable SDK/CPN evidence
persistence and committed replay remain absent. Sequential source and
predecessor observations are not one distributed transactional snapshot.
