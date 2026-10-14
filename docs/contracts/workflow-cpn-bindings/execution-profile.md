# Flat CPN semantic closure and execution profile

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Flat CPN semantics and runtime nesting

Each executable net instance MUST use one immutable, validated, flat CPN
definition and one complete marking. Reusable control fragments MAY be lowered
at compile time into that flat definition.

A child workflow is different from a compile-time fragment. A child remains a
separately compiled workflow plan with its own flat CPN definition, marking,
run, occurrences, attempts, history, and terminal outcome. The parent plan
references the child through a typed hierarchical binding. The child topology
MUST NOT be copied into the parent definition.

This is runtime nesting of separately authoritative CPN instances, not a claim
to implement the hierarchical CPN formalism of CPN Tools.

## Definition layers

The contract distinguishes three identities:

1. `CpnDefinitionIdentity` is the owner-local nominal identity of
   the flat generic CPN graph; it is not sufficient content closure.
2. `WorkflowExecutionPlanIdentity` identifies the complete executable semantic
   closure: exact canonical flat-CPN representation identity and digest, exact
   CPN execution-profile identity, initial-marking contract, payload-color
   bindings, transition routes, child bindings, terminal-delivery requirements,
   mapping descriptors, and compiler implementation/version descriptors.
3. `WorkflowExecutionBindingsIdentity` identifies one exact deployment linking
   of that plan to provider, worker, environment, resolver, and child-plan
   descriptors.

The execution-plan identity MUST be the domain-separated SHA-256 of one closed
canonical plan representation containing every semantic-closure item above. The
deployment-bindings identity MUST similarly derive from one closed canonical
binding representation and the exact execution-plan identity. Neither identity
may be caller-supplied nominal text, a mutable registry key, or an import path.
The canonical representation profiles are private candidate boundaries until a
separate compatibility decision accepts them.

A provider or environment change MUST NOT mutate the execution plan. A canonical
flat-definition byte, representation profile, CPN execution-profile identity,
payload schema, codec, transition mapping, child export, child port,
terminal-delivery requirement, companion-evidence requirement, or child-plan
change MUST change the execution-plan identity even when a nominal
`CpnDefinitionIdentity` is unchanged.

## Canonical flat definition and CPN execution profile

The plan MUST bind an immutable canonical flat-definition representation, its
representation-profile identity, and SHA-256 over its exact bytes. The canonical
representation MUST close over every semantic color, place, transition, arc,
variable, pattern, expression, priority, and selection-policy field. A nominal
`CpnDefinitionIdentity` alone is insufficient because the current
shadow kernel accepts it separately from graph content.

The plan MUST also bind one immutable `WorkflowCpnExecutionProfile` containing
exact identities for:

- admitted CPN value model, bounded control-record representation, and semantic
  version;
- closed expression grammar, including exact field-projection and
  control-record-construction variants;
- canonical definition representation and decoding;
- canonical marking, transition-binding, directive, and result representation
  and identity derivation;
- definition validation;
- marking and control-record-schema validation;
- expression and constructor evaluation;
- complete enabled-binding enumeration;
- enabled-binding ordering;
- binding selection;
- external-output validation; and
- transition firing.

Changing any profile identity MUST change the execution-profile identity and the
execution-plan identity. Replay MUST use the exact retained profile; current
registry defaults or implementation-local constants are insufficient semantic
closure.

Post-hoc validation evidence MAY bind the already-derived plan and profile
identities, but MUST NOT become an input to either identity.

## Consumer-vocabulary reconciliation

The Si-VC consumer profile uses *definition identity* for the complete semantic
closure. Under this owner contract, that term maps to
`WorkflowExecutionPlanIdentity`. It does not expand
`CpnDefinitionIdentity`, which remains the identity of the flat CPN
semantics only. Consequently:

- managed-project payload-schema and child-interface references change the
  execution-plan identity;
- a child binding names the parent flat CPN definition and transition, then the
  enclosing plan names the child binding;
- the binding MUST NOT name the enclosing plan from which its own identity is
  derived;
- post-hoc plan/export evidence binds the already-derived semantic identity and
  MUST NOT be embedded back into that identity; and
- the resulting content-identity graph remains acyclic.

The consumer phrase *firing the substitution transition creates a child launch*
maps to selection and durable reservation of the nested parent occurrence. The
parent's logical CPN firing commits only after an exact accepted child terminal
delivery. This separation preserves pure CPN firing and prevents a launch
request from masquerading as a child result.
