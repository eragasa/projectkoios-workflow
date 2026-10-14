# Pure firing vertical slice

## Objective

Prove one complete effect-free path through an external owner integration and
the authoritative CPN runtime:

```text
CPN selected binding
→ SDK firing request
→ consumer-owned firer
→ correlated SDK result
→ admitted external output binding
→ CPN firing
→ retained successor marking and history
```

## Required work

- [ ] Compile or construct one exact transition-to-firer binding.
- [ ] Create the firing request from one selected and reserved CPN binding.
- [ ] Invoke a consumer-owned integration through the SDK `Firer` ABC.
- [ ] Reject changed occurrence, attempt, binding, request, descriptor, or result
  correlation.
- [ ] Map admitted owner output to an explicit external-output binding.
- [ ] Invoke the pure CPN transition firer only after result admission.
- [ ] Atomically retain the firing evidence and successor marking under the local
  runtime's accepted persistence boundary.

The first intended consumer fixture is the
[Simulations QE artifact-set pilot](simulations/qe_artifact_set_sdk_pilot.md).
Its owner-side SDK boundary and isolated cross-wheel firing now pass, but it
correctly stops at a correlated SDK result. The SDK
[transition action binding](../../architecture/projectkoios/workflow/sdk/actions/TransitionActionBinding/)
uses the Simulations-owned `artifact_set_identity` as the opaque CPN string
output and retains the complete canonical `artifact_set` document as evidence;
the transport payload digest remains integrity evidence rather than domain
state. An experimental Workflow-owned request factory now canonically encodes the exact
ordered selected binding, derives its digest, validates request inputs and
runtime coordinates, and constructs the SDK request without accepting a claimed
digest. The paired mapper validates the exact SDK descriptors, retained context,
result metadata, canonical ASCII identity, and evidence order, then constructs
one declared shadow-CPN `STRING` binding. Neither component expands the
standalone SDK or claims the proposed full CPN-bindings contract.
[`WorkflowEngine`](../../architecture/projectkoios/workflow/runtime/WorkflowEngine/)
must still retain the mapping through an authoritative execution plan, perform
current predecessor reservation/revalidation and result admission, invoke pure
firing, and atomically retain firing evidence. No SDK record authorizes
inventing the mapping inside the owner adapter.

## Completion evidence

- [x] Record the isolated
  [experimental request-and-output mapping evidence](experimental_ascii_output_mapping_evidence.md).
- [ ] Record exact SDK, Workflow, and consumer revisions for the complete slice.
- [ ] Retain request, result, binding, firing, and history identities.
- [ ] Retain deterministic replay evidence.
- [ ] Retain negative test results for stale and mismatched results.
- [ ] Prove that the consumer firer cannot access or mutate the Workflow marking.

## Exclusions

The slice performs no filesystem staging, process launch, scheduler submission,
network call, retry, reconciliation, calculator execution, or production
migration.
