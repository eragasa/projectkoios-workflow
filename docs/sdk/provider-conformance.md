# Provider conformance profile

Status: release-candidate test protocol for providers targeting
`projectkoios/workflow/v0.1`.

This profile constrains orchestration integration. It is not a universal
application framework and does not transfer domain or scientific behavior into
Workflow.

## Provider-owned fixture

A provider repository supplies an immutable fixture containing its exact:

- workflow family, definition, source revision, and contract identities;
- canonical CPN definition produced by the provider-owned exporter;
- execution profile identity and compiled execution plan;
- child interface and export, when the workflow is callable as a child;
- payload schema, codec, media-type, and color bindings;
- provider capabilities and deterministic failure declarations;
- retained artifact references and correlation metadata.

The fixture contains no live provider objects, callbacks, filesystem paths,
resolvers, registries, or executable expressions. Workflow must not reconstruct
provider domain objects.

## Required provider tests

A provider conformance suite must demonstrate all of the following against the
installed Workflow wheel:

1. **Declared definition:** `CpnDefinitionValidator` reports no findings for the
   exact provider definition.
2. **Canonical closure:** `CpnCanonicalDefinitionCodec` round-trips exact bytes,
   identity, representation profile, and SHA-256 without normalization.
3. **Plan closure:** `WorkflowExecutionPlanCompiler` retains the exact nominal
   definition, canonical definition, execution profile, routes, mappings,
   payload bindings, child bindings, and interfaces.
4. **Child ownership:** `WorkflowChildPlanExportCorrelator` reports no mismatch
   between the separately retained child plan and provider-owned export.
5. **Static references:** `WorkflowChildPlanGraphValidator` accepts the complete
   finite parent-plan to child-plan reference set and rejects substitutions,
   unreachable references, self-reference, and cycles.
6. **Capabilities:** deployment binding construction admits every required
   provider, worker, environment, resolver, protected-effect, reconciliation,
   protocol, terminal, and companion capability and rejects one-field
   substitutions.
7. **Request/result correlation:** enablement, selection, firing, and replay bind
   the exact definition, predecessor marking, transition, directive, profile,
   external outputs, and successor identity.
8. **Payload lineage:** `WorkflowDomainPayloadReferenceAssembler` and
   `WorkflowDomainPayloadReferenceVerifier` bind exact provider bytes to the
   declared schema/media contract and retained artifact identity. Provider code,
   not Workflow, reconstructs the domain object through its explicit codec.
9. **Deterministic failure:** every admitted provider failure is routed through a
   declared closed outcome without fabricated success, cancellation, terminal,
   or scientific disposition.
10. **Installed-wheel use:** the provider tests import only the authorized
    direct-module SDK surface and pass without the Workflow source tree on
    `sys.path`.

Each substitution test changes one field at a time and retains the resulting
closed finding or failure code. A digest match alone is not conformance.

## Scientific exclusions

The suite does not test projections, physical units, nondimensionalization,
fitting, optimization, feasibility/support mathematics, QE or Wannier
behavior, numerical thresholds, scientific correctness, or scientific
acceptance. Those remain provider-owned tests and review evidence.

## LLM adapter exclusion

The core provider protocol contains no LLM provider, prompt, agent, or tool
contract. A separately authorized LLM adapter must retain its model/provider,
exact prompt/template, tool permissions, repository and branch, allowed paths,
protected-action permissions, input/output hashes, reviews, and human decision
records while emitting the same typed canonical provider requests and results.

## Release gate

The Workflow package remains `0.0.0` until at least one provider-owned canonical
artifact passes this profile, the SDK receives independent review, and release
is separately authorized. Passing this profile does not itself authorize
provider execution, migration, release, or scientific acceptance.
