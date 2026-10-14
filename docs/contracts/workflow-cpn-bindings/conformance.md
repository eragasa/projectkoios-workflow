# Ownership, conformance, and acceptance

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Managed-project and provider ownership

Generic Workflow owns:

- generic reference and binding records;
- plan-closure and deployment-link validation;
- terminal-delivery requirements and canonical companion-input ordering;
- net-instance, occurrence, attempt, delivery, and quiescence identities;
- reservation, authority admission, persistence, replay, cancellation
  coordination, and reconciliation semantics; and
- enforcement of staging-receipt prerequisites declared by a plan.

A child/provider owner owns:

- the authoritative child source definition and deterministic export;
- provider-native request, job, result, saved-state, and manifest schemas;
- source and destination byte verification;
- native job and artifact identities; and
- mechanical result and provider semantic-normalization evidence.

A managed project owns:

- parent scientific topology;
- domain payload schemas and codecs;
- scientific role, threshold, candidate, and acceptance policy;
- mapping from provider evidence to accepted project records; and
- final domain disposition.

No owner may duplicate another owner's topology or reinterpret another owner's
payload without an explicit versioned adapter.

## Consumer-profile reconciliation summary

This table records how the owner proposal treats the Si-VC requirements. It is
not contract acceptance or implementation evidence.

| Consumer requirement | Treatment in this proposal |
|---|---|
| One runtime-neutral canonical CPN | Adopted as one flat canonical CPN per net instance |
| Existing typed source records and field guards | Adopted through bounded generic control records plus closed field-projection and record-construction expressions; no live domain objects or topology-visible token splitting |
| Definition closure binds payloads and children | Adopted as `WorkflowExecutionPlanIdentity`; flat CPN identity remains narrower |
| Exact six-field `DomainPayloadReference` | Adopted without adding envelope fields |
| Strict owner codecs and canonical JSON | Adopted as pure encoding/metadata plus outer retention and pure reference assembly, all outside the CPN kernel |
| Guards never parse artifacts | Adopted without exception |
| Reference authoritative child without copied topology | Adopted through separately compiled child export and plan references |
| Durable hierarchical child instance | Adopted as runtime nesting, not live hierarchical CPN semantics |
| Child fan-out | Deferred; v0.1 requires exactly one child at canonical ordinal `0` per parent occurrence |
| Fresh loop instance versus same-occurrence retry | Adopted with distinct occurrence and attempt identities |
| Parent substitution transition | Refined: selection/reservation launches; logical firing commits after terminal delivery |
| Runtime identity ordering | Refined to request before occurrence so content derivation is acyclic |
| Provider candidate versus project acceptance | Preserved as distinct owner payload schemas |
| Terminal payload plus separately retained provider evidence | Adopted through classification-specific terminal-delivery and companion-evidence requirements without changing child topology |
| SCF-to-NSCF staging receipt barrier | Adopted and strengthened with a distinct staging effect intent and evidence |
| Persistence and complete replay | Adopted as a future outer verifier that first accepts unchanged Slice A replay, then verifies payloads, runtime safety state, and pure CPN replay |
| Cancellation, late delivery, reconciliation, and quiescence | Adopted as runtime-owned semantics |
| Concrete APIs and implementation | Still blocked and outside this proposal's authorization |

## Informative Si-VC stress-case mapping

The proposed Si-VC consumer profile exercises this generic contract as follows:

| Generic concept | Si-VC role |
|---|---|
| Parent flat CPN | 56-place/55-transition `si_vc_component_locality` net |
| Nested parent transition | `execute_scf_child` |
| Child export | simulations-owned `dft_pw_scf` source with 12 places and 8 transitions |
| Primary child terminal payload | Successful SCF terminal-outcome reference from the unchanged terminal port |
| Candidate provider companion | Separately retained post-terminal QE saved-state candidate after successful execution and verified manifest |
| Managed-project acceptance payload | accepted SCF parent binding unchanged candidate handoff to role, coordinate, normalized evidence, policy, and acceptance occurrence |
| Staging receipt | fresh attempt-scoped SCF-to-NSCF verified copy receipt |
| Dependent protected effect | exact NSCF calculator occurrence and attempt |
| Separate semantic gate | post-success NSCF QEXSD/source-frame qualification |

The authoritative simulations child currently uses SNAKES and does not yet emit
the required saved-state companion. Conformance therefore requires an
owner-controlled canonical child exporter/adapter, a success-classification
terminal-delivery requirement, and provider schema work; the companion remains
runtime evidence and the parent MUST NOT copy or modify the
twelve-place/eight-transition topology. This table is
an architecture stress case, not a Generic Workflow dependency on Si-VC or an
execution authorization.

## Required conformance vectors

An implementation claiming this contract MUST provide synthetic, payload-free
fixtures for at least:

1. canonical six-field payload-reference encode/decode and stable reference
   identity;
2. a pure owner codec producing bytes/metadata, an outer artifact operation
   supplying the retained artifact identity, and a pure assembler computing
   digest and size without codec store access or locator fabrication;
3. rejection of duplicate, unknown, missing, wrongly typed, oversized,
   noncanonical, path-bearing, digest-mismatched, and byte-size-mismatched
   references or payloads;
4. changed payload bytes, schema, media type, digest, byte size, or artifact
   identity changing the reference identity, and a changed codec/owner changing
   the execution-plan identity;
5. payload-token admission and replay rejecting wrong schema, media type,
   owner/codec resolution, maximum size, payload digest, payload byte count,
   per-complete-marking reference-count overflow, missing required token
   identity, or duplicate required token identity;
6. a guard unable to resolve, decode, or inspect payload bytes;
7. each semantic flat-definition mutation changing the canonical-definition
   digest and execution-plan identity even when its nominal definition identity
   is unchanged;
8. each value-model, definition/marking/binding/result representation,
   definition-validator, marking-validator, evaluator, enabler, ordering,
   selector, external-output-validator, and firer profile mutation changing the
   CPN execution-profile and execution-plan identities;
9. plan identity changing when a payload-color binding changes while the flat
   CPN definition identity remains unchanged;
10. child export validation against an independently stated flat child plan;
11. parent plan containing the exact child export/binding but no copied child
    place, transition, arc, guard, or inscription definitions;
12. stable child topology across different run subjects and distinct initial
    markings;
13. v0.1 compile/link rejection of child cardinality other than one or canonical
    child ordinal other than signed integer `0`;
14. fresh child instance for a later loop occurrence and no fresh child instance
    for an ambiguous retry of the same occurrence;
15. atomic retention of child-creation intent before child creation;
16. lost child-creation acknowledgement routing to reconciliation without a
    duplicate child instance;
17. wrong parent, child, definition, port, occurrence, attempt, history-head,
    mapper, or terminal-classification delivery failing closed;
18. child terminal success, known failure, and confirmed cancellation mapping
    only through declared terminal ports and normal parent firing;
19. infrastructure failure and ambiguity producing no fabricated parent firing;
20. every protected child effect requiring distinct exact-occurrence authority;
21. authority expiry or revocation blocking a later attempt;
22. cancellation/success races producing one deterministic retained terminal
    mapping;
23. late and duplicate delivery producing no second parent firing or terminal
    token;
24. quiescence withheld for active claims, attempts, cancellations, child
    processes, `STILL_AMBIGUOUS`, `EVIDENCE_INVALID`, `CONFIRMED_PARTIAL`, or
    any other unresolved state;
25. source-manifest verification, fresh-workspace copy, destination
    verification, and actual receipt retention before dependent dispatch;
26. a plan and dependent effect intent containing only the receipt-requirement
    identity, with the actual receipt first entering staging evidence and later
    dependent dispatch authority/evidence without a content-identity cycle;
27. one-file source, destination, manifest, handoff, receipt, plan, CPN profile,
    canonical definition, export, or event tamper failing closed;
28. the outer complete-replay verifier first accepting unchanged Slice A and
    each later-slice segment verifier plus continuous predecessor/ordinal bridges
    before reading artifacts or executing pure CPN replay;
29. complete replay reconstructing reservation, plan, attempt, authority,
    ambiguity, reconciliation, cancellation, receipt-barrier, child-delivery,
    terminal-commit, and quiescence semantics plus exact parent/child markings;
30. complete replay making no provider, calculator, worker-effect, or other
    external effect call during pure CPN replay;
31. runtime events and diagnostics containing no payload bodies, credentials,
    private paths, or protected excerpts; and
32. software conformance reported separately from scientific validation,
    uncertainty quantification, domain acceptance, publication, and execution
    authority;
33. every admitted terminal classification having exactly one closed delivery
    requirement, including an explicit empty companion tuple for a
    no-companion classification;
34. a changed terminal-delivery or companion requirement changing child export,
    child plan, and enclosing parent-plan identities without changing or copying
    child topology;
35. rejection of noncontiguous requirement ordinals, invalid minimum/maximum or
    total cardinality, duplicate reference use, and representation-bound
    overflow;
36. canonical mapper inputs containing the primary reference first, then
    requirements by ordinal, then references by lexical reference identity;
37. missing, excess, duplicate, wrong-role, wrong-schema, wrong-codec,
    wrong-media-type, wrong-phase, stale, cross-child, noncanonical-order, or
    correlation-failing companion evidence producing no delivery or parent
    firing, while a known-failure classification neither requires nor fabricates
    a success-only companion;
38. post-terminal companion retention failure or ambiguity preserving the child
    terminal commit while retaining the parent reservation and routing to
    reconciliation;
39. a pure output mapper receiving only already-admitted primary and companion
    inputs and making no resolver, codec, store, provider, filesystem, network,
    clock, worker, or kernel call;
40. delivery identity changing with any primary, companion, requirement,
    terminal-head, correlation, mapper, child, or parent-occurrence input while
    excluding the future parent firing identity; and
41. complete replay reconstructing companion admission, production phase,
    canonical input order, correlation, delivery assembly, ambiguity, and
    quiescence without repeating a protected effect;
42. canonical control-record encode/decode and marking admission at every type-
    definition, field, record-node, record-depth, expression-node, expression-
    depth, string, sequence, and byte bound, plus rejection one unit beyond each
    applicable bound;
43. rejection of duplicate, missing, unknown, wrongly typed, noncanonical,
    cyclic, open, wrong-record-type, and non-lexically ordered control-record
    fields and of cyclic or over-depth record-type graphs;
44. every record-type, color/type admission, field kind, field order, projection
    path, constructor field expression, value-model bound, grammar, validator,
    evaluator, external-output validator, and owner mapping-descriptor mutation
    changing the canonical-definition, execution-profile, or execution-plan
    identity to which it contributes;
45. field projection preserving matching evaluation/task identities and
    rejecting unrelated identities, and record construction preserving exact
    registration, submission, analysis, success, and known-failure outputs for
    the unchanged simulations SCF twelve-place/eight-transition fixture;
46. SCF parity retaining one control-record token for each source action, event,
    request, analyzed output, and terminal outcome without adding fact places,
    splitting one source token, moving a source guard into admission policy, or
    invoking a provider-native class or constructor inside the kernel;
47. complete replay reconstructing control records, projections, constructors,
    and successor markings with the exact retained type definitions, value
    representation, grammar, validators, evaluator, and mapping descriptors,
    while rejecting substitution of current defaults; and
48. static dependency and adversarial expression fixtures proving that no
    callable, import, source expression, reflection, arbitrary attribute,
    subscript, payload decoder, artifact resolver, domain object, or hidden
    callback can enter record validation, guard evaluation, construction,
    enablement, or firing.

Cross-repository conformance MUST identify exact contract, specification,
implementation, child-provider, and managed-project revisions plus fixture and
validation-result identities.

## Acceptance gates

This proposal is ready for acceptance review only when:

- workflow-owner review finds the flat-kernel, execution-plan, runtime, and
  persistence boundaries internally consistent;
- at least one child provider reviews and supplies a complete export/schema
  fixture without copying topology into a consumer;
- at least one managed project reviews and supplies parent binding, payload,
  terminal-correlation, and classification-specific companion fixtures;
- canonical flat-definition and every CPN execution-profile mutation vector,
  including control-record type, bound, field, projection, constructor, grammar,
  validator, evaluator, and mapping-descriptor mutations, change the execution-
  plan identity as specified;
- canonical payload-reference, pure codec/retention/assembly, and color-binding
  admission vectors pass in independent owner and consumer implementations;
- a later accepted runtime slice retains the plan, attempt, authority, effect,
  reconciliation, cancellation, receipt, terminal-commit, and quiescence records
  required by the outer complete-replay verifier;
- the unchanged simulations SCF twelve-place/eight-transition fixture passes
  field-guard, constructor-output, mismatched-identity, success, and known-failure
  parity without token splitting, topology change, or a domain callback;
- parent/child crash, ambiguity, companion-retention, cancellation,
  late-delivery, and replay vectors pass without duplicate effects, delivery
  mutation, or fabricated firing;
- artifact resolver and staging-receipt fixtures preserve privacy and exact-byte
  provenance;
- authority admission remains separate from structural enablement and child
  creation;
- dependency-direction checks keep the generic kernel and core independent of
  managed-project and provider packages; and
- implementation, migration, merge, and release remain separately authorized.

Passing these gates does not authorize protected execution or establish
scientific correctness.

## Deferred decisions

This contract does not select:

- final Python modules or public import paths;
- public wire compatibility duration;
- artifact-store technology or locator-sealing mechanism;
- the authority issuer, signature, expiry, or revocation service;
- worker pull versus authenticated control-plane push;
- queue, claim, lease, or process-supervisor implementation;
- whether operational lifecycle state uses one expanded flat net or a correlated
  companion operational CPN, provided the nested-route protocol remains
  observable and authoritative;
- database, backup, archival, or deployment technology;
- child fan-out greater than one, including set retention, per-ordinal launch,
  aggregation, cancellation, and terminal-set semantics;
- compensation policy for partially applied effects;
- provider or consumer migration order; or
- release and rollback procedures.

These choices require separate reviewed records and MUST NOT be inferred from a
consumer profile.

## Stop conditions

Stop before implementation or execution if:

- an execution plan would omit the exact canonical flat-definition digest or any
  required CPN execution-profile identity;
- a parent or deployment artifact would copy child topology;
- a raw JSON body, arbitrary mapping, native object, credential, or machine path
  would enter a CPN token or canonical runtime event;
- a codec would fabricate or retrieve an artifact identity, or an artifact store
  would be hidden inside a pure codec operation;
- a payload-reference token could enter a marking without exact color-binding,
  payload-byte, owner, codec, per-complete-marking count, and required individual
  token-identity admission checks;
- a v0.1 hierarchical binding would admit child cardinality other than one or a
  child ordinal other than signed integer `0`;
- a guard would fetch or decode an external payload, traverse anything other
  than an admitted bounded control record, or invoke an arbitrary attribute,
  subscript, callable, import, source expression, reflection facility, owner
  object, or domain constructor;
- a control record would be open, cyclic, unbounded, schema-free, contain a
  native domain object or payload body, or bypass its exact type definition,
  color/type admission, canonical decoding, or validator;
- an exporter would preserve field guards by splitting one source token into
  several topology-visible tokens, adding places/transitions, or moving the
  source guard into outer admission policy rather than using the closed
  projection/construction grammar;
- child creation could occur before durable unique-instance retention;
- ambiguous child creation or effect execution could trigger automatic
  recreation or redispatch;
- a parent transition could fire before exact child terminal correlation or
  before every classification-required companion is retained, admitted, ordered,
  and correlated;
- a companion could be treated as a child terminal token, mutate child topology
  or marking, satisfy two requirement occurrences, or enter a mapper that hides
  resolution, decoding, provider, filesystem, network, clock, or store access;
- child or parent protected effects could run without exact attempt-bound
  authority;
- a staging receipt could be created without source and destination
  verification, admitted after dependent dispatch, or embedded as a future
  identity inside the plan or dependent effect intent;
- cancellation, timeout, lease expiry, or worker loss could be treated as proof
  of non-execution;
- Slice A replay could be redefined by implication, or the outer complete replay
  verifier could call providers or substitute current definitions/profiles for
  retained ones;
- quiescence could be reported with an active child, claim, attempt,
  companion-production intent, delivery assembly, cancellation, partial
  application, invalid evidence, or unresolved ambiguity;
  or
- implementation, dependency change, provider migration, protected execution,
  commit, merge, release, or publication would begin without its separately
  required authorization.
