# Experimental pure-action CPN plan-closure evidence

## Scope

This record covers a bounded v0 plan extension that binds the existing
pure-action input plan to exact canonical flat-CPN definition bytes and an exact
candidate CPN execution-profile identity. It is not the complete proposed
`WorkflowExecutionPlan` or `WorkflowCpnExecutionProfile`.

## Implemented boundary

- `ExperimentalWorkflowCpnDefinitionEncoder` encodes every current shadow-CPN
  color, place, transition, arc, selection-policy, priority, guard, input
  pattern, output template, literal, and variable-expression field as bounded
  canonical UTF-8 JSON.
- The encoder has an explicit immutable representation-profile identity and
  rejects over-depth guards, oversized text, excessive collections, and an
  oversized complete representation.
- Integers use decimal strings, finite real values use `float.hex()`, and tuple
  values remain ordered arrays, avoiding JSON number ambiguity.
- `ExperimentalWorkflowCpnExecutionProfile` content-identifies the exact named
  value, grammar, validation, evaluation, enablement, ordering, selection,
  external-output-validation, and transition-firing components used by this
  bounded candidate.
- `ExperimentalWorkflowPureActionCpnPlanFactory` requires a structurally valid
  definition, verifies its nominal definition and transition against the
  existing input plan, and derives a plan identity from the input-plan identity,
  exact definition bytes and digest, representation profile, and execution
  profile.
- The plan record validates canonical JSON, schema/profile agreement, nominal
  definition identity, byte bounds, digest, and exact profile reconstruction.
- The predecessor reservation now optionally binds the CPN-plan identity under
  a new v0 identity domain. Earlier base, input-admission, and source-authorized
  reservation shapes retain their original identities.
- Pure CPN firing requires the plan-bound reservation, exact input-plan identity,
  exact canonical definition bytes, and the currently supported execution
  profile before calling the CPN firer.

## Adversarial evidence

Focused tests prove that changing definition content while retaining the same
nominal definition identity changes the definition digest and CPN-plan identity;
changing a firing-profile component changes the plan identity; the reservation
binds the exact CPN plan; and substituting a different definition plan after
reservation fails before firing.

Validation from the uncommitted candidate on base Workflow revision `d4a8f11`:

- focused authority/admission/reservation/invocation/plan/firing tests:
  `42 passed`;
- full Workflow suite: `362 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `50` source files;
- Ruff, formatting of changed sources, architecture, runtime dependency,
  shadow-provenance, documentation-link, and diff checks: passed;
- CPN plan-closure source SHA-256:
  `d7b4b017baaa52b5350ced11a1158c36af34547381a44350fdeb7bfc3ce979ea`;
- evolved reservation source SHA-256:
  `a2b044cb5cd15fc79c72f08eb4701a5b009b33e9f4008476b8d893f44479b615`;
- focused test source SHA-256:
  `f2a21c9f935936f2b5c7a98e0cab9735c4bc0f04b84ae5be76b7b999fc5260a5`;
- two Workflow wheels built with `SOURCE_DATE_EPOCH=315532800` were
  byte-identical, SHA-256
  `c3b40d3e980a2a2f5123806439ecd6113e500f639a78520499e5bc5832b4d810`.

Deterministic successful fixture identities:

- canonical definition SHA-256:
  `1344efeb8246cdef7d0bf720dd1ac06f08663ff9ca95bc93d88fe380a0d42234`;
- candidate CPN execution profile:
  `3321f8a87314f964af4a8fb1c8cc732e80c2b7686f1f2fbe68329d708d931173`;
- CPN plan:
  `ccfe9ca78f04da9167ef8237d81ccf048d1f09cf6765b8b8210ca7774f16b982`;
- CPN-plan-bound reservation:
  `e187f49155f936daef44e5a22025a00e522aff689b9c39daff1b315ff2f64c7c`.

## Remaining gaps

This original candidate did not define canonical decode/reconstruction for
retained definition bytes or a canonical semantic-marking representation. The
later [canonical CPN representation decoding evidence](canonical_cpn_representation_decoding_evidence.md)
adds those bounded reconstruction primitives without changing this candidate's
identity vectors. Canonical CPN firing-result representation, retained
representation-bundle persistence, every profile component required by the
proposed umbrella contract, payload-color bindings, routes, child bindings,
terminal delivery, and compiler descriptors remain incomplete. It therefore
cannot claim complete
`WorkflowExecutionPlan`, `WorkflowExecutionBindings`, replay, or
`projectkoios.workflow.cpn-bindings` conformance.

A later in-memory atomic-commit candidate now consumes the reservation and
advances compact marking coordinates, but durable persistence, crash recovery,
and committed replay remain absent.
