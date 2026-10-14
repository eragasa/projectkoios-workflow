# Persistence and complete replay

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Persistence and replay

Canonical history MUST retain compact identities and payload references, not
payload bodies, native files, credentials, or machine paths.

Parent and child histories MUST be independently verifiable and connected by
retained child-creation, child-instance, terminal-delivery, and parent-firing
evidence. A mutable projection MUST NOT manufacture or repair those links.

`WorkflowCpnBindingsCompleteReplayVerifier` is a future outer verifier. It is
not the bounded Slice A replay subject defined by
`projectkoios.workflow.runtime@0.1.0`, and this proposal does not expand Slice A
by implication. The outer verifier MUST first invoke and accept unchanged Slice
A identity-chain replay, which performs no artifact read or CPN execution, over
the exact event schema/segment owned by Slice A. Each subsequent event-schema
segment MUST be verified by its separately accepted later-slice verifier, and
the outer verifier MUST verify the predecessor/ordinal bridge between segments.

After successful Slice A verification, complete CPN-bindings replay MUST:

1. use the exact retained canonical flat definitions, control-record type
   definitions, value-model and expression-grammar profiles, CPN execution
   profiles, execution plans, and deployment-binding evidence rather than
   current registry entries;
2. resolve every required payload reference through a read-only immutable
   artifact boundary;
3. verify reference identity, color-binding agreement, payload byte size, and
   SHA-256 before decoding;
4. invoke only the exact retained schema-version codec and reject noncanonical
   or semantically invalid payloads;
5. reconstruct and verify the runtime safety state machine, including:
   - request retention and active-occurrence reservation ownership;
   - deterministic occurrence order and exact selected CPN binding;
   - child-create intent retention before child creation;
   - plan retention before any dispatch authorization;
   - bounded attempt and claim/lease identity where applicable;
   - exact attempt-bound authority before every worker call;
   - execution or ambiguity evidence before outcome processing;
   - reconciliation before any retry after ambiguity;
   - separately authorized cancellation and its observed result;
   - actual staging-receipt retention before dependent dispatch authority;
   - exact terminal classification and requirement selection;
   - primary and canonical ordered companion admission, retention phase,
     correlation, and delivery assembly before parent logical firing;
   - exact child terminal delivery before parent logical firing;
   - terminal parent commit before projection advancement; and
   - terminal resolution of every admitted child, attempt, cancellation, and
     ambiguity before quiescence;
6. reconstruct child-instance, primary terminal payload, companion-evidence,
   terminal-delivery, and parent-delivery correlations, including exact canonical
   mapper-input order;
7. replay pure CPN control-record validation, field projection, record
   construction, enablement, ordering, selection, external-output validation,
   and firing with the exact retained value model, grammar, validators,
   evaluator, and CPN execution profile, without provider, worker, artifact
   resolver, owner codec, domain constructor, callback, clock, filesystem, or
   calculator calls inside the CPN kernel; and
8. compare reconstructed markings, terminal outcomes, lifecycle state, and
   quiescence evidence with retained identities.

Payload resolution and decoding are a bounded outer preverification phase, not
Slice A replay and not CPN guard or firing behavior. A structural diagnostic MAY
omit owner payload resolution or full runtime-state reconstruction, but it MUST
be labeled incomplete and MUST NOT claim complete replay, semantic payload
verification, or safety-state verification.

Missing required runtime records, payloads, reference documents, CPN profiles,
unsupported codecs or schemas, changed child exports, plan-closure mismatches,
missing or ambiguous companion evidence, corrupt receipts, or unavailable
retained evidence MUST fail closed. Neither
Slice A nor the outer verifier may silently upgrade a schema, substitute a
current definition or child plan, repair history, or repeat an external effect.
