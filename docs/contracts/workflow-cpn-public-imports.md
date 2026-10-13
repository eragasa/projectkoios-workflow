# Workflow CPN public import inventory

Status: owner candidate accompanying `projectkoios/workflow/v0.1`.

This candidate inventory records the proposed semantic owner modules. It does
not establish an implementation binding or authorize consumer imports. Package `__init__.py` files intentionally export
no objects. They are namespace boundaries, not aggregate facades; consumers
must not depend on incidental transitive imports.

## Execution and transport

| Semantic owner | Candidate module |
|---|---|
| Generic values and control-record type definitions | `projectkoios.workflow.petrinet.colored.values` |
| Flat CPN graph definitions and graph identities | `projectkoios.workflow.petrinet.colored.definitions` |
| Markings, places, tokens, and marking identities | `projectkoios.workflow.petrinet.colored.markings` |
| Ordered transition bindings | `projectkoios.workflow.petrinet.colored.bindings` |
| Enablement outcomes and semantic identities | `projectkoios.workflow.petrinet.colored.enablement.outcomes` |
| Enablement-result identity derivation | `projectkoios.workflow.petrinet.colored.enablement.identity_derivation` |
| Enablement-failure construction | `projectkoios.workflow.petrinet.colored.enablement.failure_building` |
| Enabled-binding ordering | `projectkoios.workflow.petrinet.colored.enablement.ordering` |
| Complete transition enablement | `projectkoios.workflow.petrinet.colored.enablement.transitions` |
| Deterministic or directed selection | `projectkoios.workflow.petrinet.colored.selection` |
| Complete firing inputs | `projectkoios.workflow.petrinet.colored.firing.inputs` |
| Firing occurrence and output audits | `projectkoios.workflow.petrinet.colored.firing.audits` |
| Firing outcomes | `projectkoios.workflow.petrinet.colored.firing.outcomes` |
| Token-occurrence reconstruction | `projectkoios.workflow.petrinet.colored.firing.occurrence_reconstruction` |
| Firing-result identity derivation | `projectkoios.workflow.petrinet.colored.firing.identity_derivation` |
| Successor-marking construction | `projectkoios.workflow.petrinet.colored.firing.successor_marking` |
| Firing-failure construction | `projectkoios.workflow.petrinet.colored.firing.failure_building` |
| Pure transition firing | `projectkoios.workflow.petrinet.colored.firing.transitions` |
| External-output admission | `projectkoios.workflow.petrinet.colored.external_outputs` |
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
| Firing transport identity contracts | `projectkoios.workflow.petrinet.colored.canonical.firing_contracts` |
| Firing results and pure replay | `projectkoios.workflow.petrinet.colored.canonical.firings` |

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
- `projectkoios.workflow.petrinet.colored.control.records.type_graph`
- `projectkoios.workflow.petrinet.colored.control.records.schema`
- `projectkoios.workflow.petrinet.colored.control.records.value_canonical`
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
| Child interfaces and terminal delivery | `projectkoios.workflow.petrinet.colored.children.interfaces` |
| Hierarchical child bindings | `projectkoios.workflow.petrinet.colored.children.bindings` |
| Child-export definition records | `projectkoios.workflow.petrinet.colored.children.exports.definition` |
| Child-export identity derivation and exporter | `projectkoios.workflow.petrinet.colored.children.exports.canonical` |
| Post-hoc child-export conformance evidence | `projectkoios.workflow.petrinet.colored.children.exports.evidence` |
| Static child-plan references and cycle validation | `projectkoios.workflow.petrinet.colored.deployments.linking` |
| Deployment descriptors and execution bindings | `projectkoios.workflow.petrinet.colored.deployments.bindings` |
| Cross-artifact closure correlation | `projectkoios.workflow.petrinet.colored.closure_validation` |

## Shadow execution

Immutable shadow firing contracts are owned by
`projectkoios.workflow.petrinet.colored.shadow.contracts`; the firing action is
owned by `projectkoios.workflow.petrinet.colored.shadow.firing`. Immutable replay
contracts are owned by
`projectkoios.workflow.petrinet.colored.shadow.replay_contracts`; the replay
action is owned by `projectkoios.workflow.petrinet.colored.shadow.replay`.

These imports expose software contracts only. They do not authorize provider
execution, consumer migration, dependency changes, release, scientific
acceptance, or use of a child export whose exact evidence binding has not passed
deployment linking.
