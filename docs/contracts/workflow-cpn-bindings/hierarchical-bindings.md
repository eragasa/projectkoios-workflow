# Parent hierarchical bindings

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Parent hierarchical binding

## `WorkflowHierarchicalChildBinding`

The parent execution plan MUST contain one binding for each nested route. The
binding MUST identify:

- exact parent flat CPN definition and transition-mapping identities;
- exact child export and child execution-plan identities;
- parent input place/color and child input-port mapping descriptor;
- for every admitted terminal classification, the exact child terminal-delivery
  requirement and parent external-output mapping descriptor;
- exact primary, companion, input, and output payload schema/codec identities;
- child-instance cardinality, which MUST equal exactly one in contract v0.1;
- the sole canonical child ordinal, which MUST be signed integer `0`;
- admitted child terminal classifications;
- cancellation propagation policy identity;
- quiescence requirement;
- correlation and output bounds; and
- binding contract version.

The binding and all mapping descriptors contribute to the parent execution-plan
identity. A v0.1 compiler or linker MUST reject any child-instance cardinality
other than one or any ordinal other than `0`; child fan-out is unsupported. The
binding MUST NOT contain that enclosing execution-plan identity, because doing
so would create a content-identity cycle. The child flat topology does not become
part of the parent flat CPN definition and MUST NOT be reproduced in parent
source, plan, or deployment bindings.

Deployment linking MUST prove exact agreement among parent plan, child export,
child plan, terminal-delivery and companion requirements, mapper and correlation
descriptors, provider capabilities, protocol versions, and required child-export
evidence bindings. A deployment MUST reject an admitted classification for which
the linked provider cannot supply every required companion role in its declared
phase and bounds. The transitive child-plan/export graph MUST be finite and
acyclic; recursive child-plan references are invalid in this contract version.
Discovery by matching names, annotations, nearby registry entries, or Python
subclass relationships is prohibited.

## Child-instance identity

`WorkflowChildNetInstanceIdentity` MUST derive from at least:

- parent run and net-instance identities;
- parent execution-plan identity;
- hierarchical-binding identity;
- parent transition-occurrence identity;
- exact selected parent binding and reservation evidence; and
- the v0.1 sole canonical child ordinal `0`.

A managed project MUST NOT mint the child instance or parent occurrence
identity. A repeated CPN loop activation creates a new parent occurrence and a
new child instance. An operational retry under an unchanged occurrence creates
a new attempt and MUST NOT create another child instance while original launch
status is ambiguous.
