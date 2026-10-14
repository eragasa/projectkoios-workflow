# Nested-route runtime protocol

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Nested-route runtime protocol

A nested route MUST follow this durable protocol:

1. Pure CPN enablement and selection identify one exact parent transition
   binding at one exact marking revision.
2. The runtime creates and retains the parent occurrence and exact reservation.
3. The pure input mapper produces the child initial-input references from the
   selected binding and occurrence context.
4. The runtime retains a child-creation intent and the unique child-instance
   identity before attempting child creation.
5. Child creation is idempotent for that identity. An indeterminate create
   enters reconciliation; it MUST NOT create another child instance.
6. The child starts from the exact exported plan and a validated initial marking
   correlated to the parent occurrence.
7. The parent logical transition remains reserved and unfired while the child is
   nonterminal or its classification-specific delivery is incomplete.
8. After retaining the exact terminal outcome and history head, the runtime
   selects the sole compiled terminal-delivery requirement for that
   classification.
9. The runtime durably correlates and admits the primary terminal reference and
   every required companion reference. Post-terminal production follows a
   retained idempotent intent and the normal authority/reconciliation protocol.
10. The runtime constructs and retains one identity-bound terminal delivery only
    after exact phase, cardinality, order, schema/codec, and correlation checks
    pass.
11. The pure output mapper consumes the already-admitted primary and canonical
    ordered companion inputs and produces the parent's exact external-output
    binding without resolving or decoding an artifact.
12. The runtime revalidates the reservation and atomically records the one
    parent CPN firing and terminal nested-route evidence bound to the retained
    delivery identity.

The child terminal classification MAY represent success, known failure,
cancellation, or another definition-declared terminal outcome. Each
classification has its own closed companion requirements; a success-only
companion MUST NOT be required for or fabricated on a known-failure route.
Mapping a child-workflow terminal outcome and its required evidence into a
neutral parent child-outcome token does not grant parent-domain acceptance. A
separate guarded parent transition MUST classify or accept it.

Infrastructure failure, ambiguous child creation, corrupt child history,
missing or ambiguous companion retention, mismatched delivery, unresolved
cancellation, or nonquiescent child state MUST NOT fire the parent logical
transition. Such conditions remain operational failure or reconciliation
evidence until an explicit compiled route handles them.

No runtime may inject a child result or companion directly into a parent
transition. They enter only through the retained terminal delivery, declared
external-output mapping, and normal pure firing boundary.

## Runtime identities and correlation

The runtime MUST preserve distinct nominal identities for:

| Identity | Required correlation |
|---|---|
| Workflow run | Exact execution plan, initial marking, and subject |
| Net instance | Root run or exact parent-child instance relationship |
| Request | Run, expected prior state/revision, operation intent, ordered input references, actor/authority references, bounds, and idempotency identity |
| Transition occurrence | Request plus net instance, definition, marking revision, transition, ordered binding, and exact token reservation |
| Plan | Occurrence, mapping/configuration, ordered effect intents, bounds, and runtime version |
| Effect intent | Occurrence, operation kind, exact inputs, expected evidence, and ordinal |
| Attempt | Occurrence and bounded attempt ordinal |
| Dispatch authorization | Exact occurrence, attempt, plan, intent, authority decision, scope, and validity observation |
| Execution evidence | Exact attempt, authorization, worker/provider, request, and observed result |
| Child instance | Parent occurrence, child binding, and child ordinal |
| Delivery | Exact child outcome/history head, primary terminal reference, canonical ordered companion references, requirement/mapping descriptors, and intended parent occurrence |
| Reconciliation | Exact ambiguous attempt, original idempotency/start identity, retained evidence, and query result |
| Cancellation | Exact target instance/attempt, authority, request identity, and observed result |
| Quiescence | Exact admitted child, attempt, and terminal-delivery assembly set with terminal/reconciled evidence |

Identity derivations MUST be acyclic. Logical identities, payload-reference
identities, artifact digests, and execution-evidence identities MUST remain
distinct even when one record references all of them.

A delivery from another definition, child instance, occurrence, attempt,
terminal history head, parent occurrence, terminal-delivery requirement,
companion requirement, correlation descriptor, or mapping descriptor MUST be
rejected or routed to reconciliation. A missing, excess, stale, cross-child,
wrong-phase, or ambiguously retained companion has the same fail-closed result.
Lexical similarity and equal domain payloads are insufficient correlation.

## Cancellation, late delivery, and quiescence

A parent cancellation/finalization policy MUST identify the admitted child set
from retained history. After finalization begins, the runtime MUST reject new
child admission.

Every admitted child MUST reach one of:

- accepted quiescent terminal outcome;
- provider-confirmed cancellation followed by a definition-declared terminal
  outcome and evidence that no child process remains active; or
- a terminal reconciliation disposition that establishes either
  `CONFIRMED_NOT_APPLIED` with no later attempt admitted, or
  `CONFIRMED_APPLIED` with its retained result processed to a
  definition-declared terminal outcome and operational containment.

`STILL_AMBIGUOUS`, `EVIDENCE_INVALID`, `CONFIRMED_PARTIAL`, a merely requested
cancellation, or another partial/unresolved result is not terminal containment
and cannot satisfy this rule.

Late and duplicate deliveries or companions MAY be retained as evidence.
Acceptance MUST be idempotent by exact delivery and parent-occurrence identity.
A late companion MUST NOT mutate an already accepted delivery; a late delivery
MUST NOT recreate a consumed parent active token, create a second parent firing,
select another terminal outcome, or enable post-terminal domain work.

The runtime MAY emit parent quiescence evidence only when every admitted child
has one of the terminal outcomes above, every required terminal-delivery
assembly is either accepted exactly once or terminally reconciled without parent
firing, and no active claim, attempt, companion-production intent, delivery
assembly, cancellation, child process, `STILL_AMBIGUOUS`, `EVIDENCE_INVALID`,
`CONFIRMED_PARTIAL`, or other unresolved result remains. A child terminal commit
alone is insufficient when its classification requires companion evidence. A
reconciliation record is insufficient unless it establishes the permitted
terminal disposition. Quiescence does not imply domain success.
