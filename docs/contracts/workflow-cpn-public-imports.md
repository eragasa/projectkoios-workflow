# Workflow CPN public import inventory

Status: authorized release-candidate SDK import inventory accompanying
`projectkoios/workflow/v0.1`.

The direct semantic-owner modules below are the supported SDK evaluation
imports. This decision authorizes source and installed-wheel evaluation against
the documented surface; it does not authorize consumer migration, provider
execution, scientific acceptance, or package release. Compatibility remains
release-candidate until the provider trial and release gate complete. Package
`__init__.py` files intentionally export no objects. They are namespace
boundaries, not aggregate facades; consumers must not depend on incidental
transitive imports. Compound semantic owners use nested noun namespaces rather
than compound module names. A repository gate rejects concrete import facades
and modules whose import declarations occupy more than one quarter of their
physical source lines. This is a structural ownership signal, not proof that a
module's semantics or dependency direction are correct.

The machine-readable operation and public-signature inventory is
[`../sdk/operation-manifest.json`](../sdk/operation-manifest.json). Exact
human/LLM usage and error semantics are documented in
[`../sdk/quickstart.md`](../sdk/quickstart.md) and
[`../sdk/error-handling.md`](../sdk/error-handling.md).

## Execution and transport

| Semantic owner | Candidate module |
|---|---|
| Generic values and control-record type definitions | `projectkoios.workflow.petrinet.colored.values` |
| Flat CPN graph definitions and graph identities | `projectkoios.workflow.petrinet.colored.definitions` |
| Markings, places, tokens, and marking identities | `projectkoios.workflow.petrinet.colored.markings` |
| Ordered transition bindings | `projectkoios.workflow.petrinet.colored.bindings` |
| Enablement results and semantic identities | `projectkoios.workflow.petrinet.colored.enablement.results.definition` |
| Enablement-result identity derivation | `projectkoios.workflow.petrinet.colored.enablement.results.identity` |
| Enablement-failure construction | `projectkoios.workflow.petrinet.colored.enablement.failures.building` |
| Enabled-binding ordering | `projectkoios.workflow.petrinet.colored.enablement.ordering` |
| Complete transition enablement | `projectkoios.workflow.petrinet.colored.enablement.transitions` |
| Deterministic or directed selection | `projectkoios.workflow.petrinet.colored.selection` |
| Complete firing inputs | `projectkoios.workflow.petrinet.colored.firing.inputs` |
| Firing occurrence and output audits | `projectkoios.workflow.petrinet.colored.firing.audits` |
| Firing results | `projectkoios.workflow.petrinet.colored.firing.results.definition` |
| Token-occurrence reconstruction | `projectkoios.workflow.petrinet.colored.firing.occurrences.reconstruction` |
| Firing-result identity derivation | `projectkoios.workflow.petrinet.colored.firing.results.identity` |
| Successor-marking construction | `projectkoios.workflow.petrinet.colored.firing.markings.successor` |
| Firing-failure construction | `projectkoios.workflow.petrinet.colored.firing.failures.building` |
| Pure transition firing | `projectkoios.workflow.petrinet.colored.firing.transitions` |
| External-output admission | `projectkoios.workflow.petrinet.colored.outputs.external` |
| Definition validation | `projectkoios.workflow.petrinet.colored.validation.definitions` |
| Marking validation | `projectkoios.workflow.petrinet.colored.validation.markings` |
| Validation findings | `projectkoios.workflow.petrinet.colored.validation.findings` |

| Canonical representation | Candidate module |
|---|---|
| Strict canonical JSON | `projectkoios.workflow.petrinet.colored.canonical.json` |
| Flat definitions | `projectkoios.workflow.petrinet.colored.canonical.definitions` |
| Markings | `projectkoios.workflow.petrinet.colored.canonical.markings` |
| Transition bindings | `projectkoios.workflow.petrinet.colored.canonical.bindings` |
| Selection directives | `projectkoios.workflow.petrinet.colored.canonical.directives` |
| Enablement results | `projectkoios.workflow.petrinet.colored.canonical.enablement` |
| Selection results | `projectkoios.workflow.petrinet.colored.canonical.selections` |
| Firing-result transport identity | `projectkoios.workflow.petrinet.colored.canonical.firing.results.identity` |
| Firing-result documents | `projectkoios.workflow.petrinet.colored.canonical.firing.results.documents` |
| Firing-result canonical replay codec | `projectkoios.workflow.petrinet.colored.canonical.firing.results.codec` |

The expression owners are:

- `projectkoios.workflow.petrinet.colored.expressions.grammar`
- `projectkoios.workflow.petrinet.colored.expressions.errors`
- `projectkoios.workflow.petrinet.colored.expressions.projection`
- `projectkoios.workflow.petrinet.colored.expressions.construction`
- `projectkoios.workflow.petrinet.colored.expressions.validation`
- `projectkoios.workflow.petrinet.colored.expressions.collection`
- `projectkoios.workflow.petrinet.colored.expressions.evaluation`
- `projectkoios.workflow.petrinet.colored.canonical.expressions.errors`
- `projectkoios.workflow.petrinet.colored.canonical.expressions.values`
- `projectkoios.workflow.petrinet.colored.canonical.expressions.guards`

The control-record owners are:

- `projectkoios.workflow.petrinet.colored.control.records.findings`
- `projectkoios.workflow.petrinet.colored.control.records.types.graph`
- `projectkoios.workflow.petrinet.colored.control.records.schema`
- `projectkoios.workflow.petrinet.colored.control.records.values.canonicalization`
- `projectkoios.workflow.petrinet.colored.control.records.values.decoding`
- `projectkoios.workflow.petrinet.colored.control.records.ordering`
- `projectkoios.workflow.petrinet.colored.control.records.canonical`

## Plans, children, and deployment linking

| Semantic owner | Candidate module |
|---|---|
| Execution-profile values and profile identity derivation | `projectkoios.workflow.petrinet.colored.profiles.definition` |
| Reviewed local profile construction and component resolution | `projectkoios.workflow.petrinet.colored.profiles.defaults` |
| Execution plans and compiler | `projectkoios.workflow.petrinet.colored.plans.definition` |
| Execution-plan identity value | `projectkoios.workflow.petrinet.colored.plans.identities` |
| Transition routes | `projectkoios.workflow.petrinet.colored.routes.transitions` |
| Owner value mappings | `projectkoios.workflow.petrinet.colored.mappings.values` |
| Payload/color bindings | `projectkoios.workflow.petrinet.colored.payloads.bindings` |
| Retained owner-payload reference values | `projectkoios.workflow.petrinet.colored.payloads.references.definition` |
| Canonical payload-reference transport | `projectkoios.workflow.petrinet.colored.payloads.references.canonical` |
| Payload-reference assembly | `projectkoios.workflow.petrinet.colored.payloads.references.assembly` |
| Exact-byte payload-reference verification | `projectkoios.workflow.petrinet.colored.payloads.references.verification` |
| Child interfaces and terminal delivery | `projectkoios.workflow.petrinet.colored.children.interfaces` |
| Hierarchical child bindings | `projectkoios.workflow.petrinet.colored.children.bindings` |
| Child-export definition records | `projectkoios.workflow.petrinet.colored.children.exports.definition` |
| Child-export identity derivation and exporter | `projectkoios.workflow.petrinet.colored.children.exports.canonical` |
| Post-hoc child-export conformance evidence | `projectkoios.workflow.petrinet.colored.children.exports.evidence` |
| Static child-plan references and cycle validation | `projectkoios.workflow.petrinet.colored.deployments.linking` |
| Deployment descriptors and execution bindings | `projectkoios.workflow.petrinet.colored.deployments.bindings` |
| Cross-artifact closure correlation | `projectkoios.workflow.petrinet.colored.closure.validation` |

## Shadow execution

Immutable shadow firing contracts are owned by
`projectkoios.workflow.petrinet.colored.shadow.contracts`; the firing action is
owned by `projectkoios.workflow.petrinet.colored.shadow.firing`. Immutable replay
contracts are owned by
`projectkoios.workflow.petrinet.colored.shadow.replay.contracts`; the replay
action is owned by `projectkoios.workflow.petrinet.colored.shadow.replay.action`.

These direct imports are authorized for SDK evaluation only. They do not
authorize provider execution, consumer migration, dependency changes, release,
scientific acceptance, or use of a child export whose exact evidence binding
has not passed deployment linking.
