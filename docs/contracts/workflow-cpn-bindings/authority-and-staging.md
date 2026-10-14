# Authority, artifact resolution, and staging receipts

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Authority and protected effects

Child creation does not transfer or manufacture effect authority. Every
protected effect in a child MUST receive its own Workflow-verified, exact
occurrence-and-attempt dispatch authorization under the runtime contract.
Parent authority MUST NOT be inherited by child transitions unless the external
authority owner explicitly issued matching separately scoped evidence.

An authority admission MUST be single-use and bind exact plan, effect intent,
attempt, worker/provider scope, inputs, limits, and validity observation.
Possession of a payload reference, child export, executable path, manifest,
prior result, test marker, or enabled token does not grant authority.

Cancellation that may affect an external process is a separate protected
operation. Missing acknowledgement, timeout, lease expiry, worker loss, or
parent termination is not proof that cancellation or non-execution occurred.

## Artifact resolution and staging receipts

## Resolver boundary

The control plane and CPN kernel retain only typed content-addressed references.
An isolated authorized worker resolves artifact identities to provider-local
locators. The worker MUST verify the resolved source against the retained
reference before using it and MUST NOT return private paths in canonical
Workflow events or CPN tokens.

## `WorkflowArtifactStagingReceipt`

A plan MAY declare a
`WorkflowArtifactStagingReceiptRequirement` before dispatch of a dependent
effect. The immutable requirement descriptor binds the permitted receipt schema
and codec, source roles, staging effect-intent ordinal, dependent effect-intent
ordinal, validation predicate, and contract version. The plan and dependent
effect intent name this requirement identity only; they MUST NOT name a future
actual receipt.

Staging that writes a workspace is itself an effect intent and requires its own
applicable attempt-bound authority under the owning policy. After staging, the
typed receipt payload MUST bind:

- receipt schema and codec identities;
- exact staging-receipt requirement identity;
- source accepted-parent or source-set payload reference;
- source manifest payload reference;
- dependent occurrence, request, plan, and attempt identities;
- exact staging effect-intent and dependent execution effect-intent identities;
- staging authority identity;
- fresh attempt-scoped destination workspace/artifact-set identity;
- copied artifact count and total byte count;
- source-verification and destination-verification evidence identities;
- worker and implementation identities;
- closed staging disposition; and
- receipt contract version.

The receipt MUST NOT contain a private path. A successful disposition requires
verification of every and only manifest-declared regular file at both source
and destination. Links, path traversal, special files, undeclared files,
pre-existing destination collisions, count/size-limit violations, and digest
mismatches MUST fail closed.

The staging execution-evidence event identifies the resulting receipt reference;
the receipt MUST NOT identify that post-hoc event, which would create a
content-identity cycle. The receipt MAY safely identify the already-derived
plan, requirement, occurrence, attempt, and effect intents.

The runtime MUST durably retain the exact receipt reference and verify it against
the plan's requirement before it may admit the dependent effect's dispatch
authorization. The dependent effect intent identifies only the prior requirement;
the later dispatch authorization and execution evidence MUST identify the actual
receipt. The derivation is therefore acyclic:

```text
plan -> effect intents + receipt requirement
     -> staging authority/evidence -> actual receipt
     -> dependent dispatch authority/evidence
```

A staging exception or indeterminate write cannot be represented as a successful
receipt; it retains the occurrence reservation and enters staging reconciliation
before any restaging or dependent dispatch.

A staging receipt establishes a verified transfer relationship. It does not by
itself establish the semantic adequacy, scientific validity, or completeness of
the source or resulting calculation.
