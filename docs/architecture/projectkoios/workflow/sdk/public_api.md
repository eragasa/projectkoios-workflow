# Workflow SDK `0.1.0a1` authorized public API inventory

## Status

The Project Koios operator authorized this type inventory for the first
pure-firing SDK alpha. The inventory and its separately authorized canonical
serialization are now implemented and have standalone conformance evidence.
This does not release the SDK or permit an external owner dependency.

## Package root

Distribution: `projectkoios-workflow-sdk`

Import root: `projectkoios.workflow_sdk`

The package root exports only:

- `WORKFLOW_SDK_CONTRACT_ID`, equal to `projectkoios.workflow.sdk`; and
- `WORKFLOW_SDK_VERSION`, equal to `0.1.0a1`.

Public classes are imported from their owning modules rather than re-exported
through one flat facade.

## Alpha hard limits

The `0.1.0a1` validation contract fixes these limits even though their private
implementation constants are not public imports:

| Boundary | Limit |
|---|---:|
| Identity ASCII bytes | 512 |
| Role/token ASCII bytes | 128 |
| General descriptor text ASCII bytes | 512 |
| Media-type ASCII bytes | 255 |
| Contracts per descriptor or firer descriptors per manifest | 64 |
| Inline payloads per collection | 64 |
| Bytes per inline payload | 4 MiB |
| Aggregate payload bytes per request or result | 16 MiB |
| Reason or failure codes | 64 |
| Canonical SDK JSON document bytes | 32 MiB |
| Canonical SDK JSON nesting depth | 16 |
| Integer range | nonnegative signed 64-bit |

A consumer must declare a bound no larger than the applicable SDK limit and may
select a stricter owner or integration bound. These values can change only with
a different SDK contract version.

## `projectkoios.workflow_sdk.identities`

The module exports these distinct frozen, slotted nominal records, each with one
`value: str` field:

- `WorkflowFirerIdentity`;
- `WorkflowFirerImplementationIdentity`;
- `WorkflowTransitionBindingIdentity`;
- `WorkflowDefinitionIdentity`;
- `WorkflowNetInstanceIdentity`;
- `WorkflowTransitionIdentity`;
- `WorkflowMarkingIdentity`;
- `WorkflowOccurrenceIdentity`;
- `WorkflowAttemptIdentity`;
- `WorkflowFiringRequestIdentity`;
- `WorkflowFiringResultIdentity`;
- `WorkflowIntegrationIdentity`;
- `WorkflowIntegrationManifestIdentity`;
- `WorkflowPayloadOwnerIdentity`;
- `WorkflowPayloadTypeIdentity`;
- `WorkflowPayloadSchemaIdentity`;
- `WorkflowPayloadCodecIdentity`; and
- `WorkflowPayloadRepresentationIdentity`.

There is no public universal identity base, identity registry, runtime
class-object dispatch, generic identity codec, or conversion among nominal
identity classes. A private validator may enforce the common lexical boundary.
Identity values are exact built-in, nonempty, bounded, stripped ASCII strings
without controls or machine paths.

## `projectkoios.workflow_sdk.payloads`

### `WorkflowPayloadContract`

Frozen and slotted fields:

- `role: str`;
- `owner_identity: WorkflowPayloadOwnerIdentity`;
- `payload_type_identity: WorkflowPayloadTypeIdentity`;
- `schema_identity: WorkflowPayloadSchemaIdentity`;
- `codec_identity: WorkflowPayloadCodecIdentity`;
- `representation_identity: WorkflowPayloadRepresentationIdentity`;
- `media_type: str`; and
- `maximum_byte_length: int`.

### `WorkflowInlinePayload`

Frozen and slotted fields:

- `role: str`;
- `owner_identity: WorkflowPayloadOwnerIdentity`;
- `payload_type_identity: WorkflowPayloadTypeIdentity`;
- `schema_identity: WorkflowPayloadSchemaIdentity`;
- `codec_identity: WorkflowPayloadCodecIdentity`;
- `representation_identity: WorkflowPayloadRepresentationIdentity`;
- `media_type: str`;
- `payload: bytes`;
- `byte_length: int`; and
- `payload_sha256: str`.

Construction requires exact metadata types, a nonempty bounded built-in `bytes`
payload, `byte_length == len(payload)`, and lowercase SHA-256 equal to
`SHA256(payload)`. The digest covers the payload bytes only. The payload excludes
its own digest, Workflow envelope identity, authority, credentials, machine
paths, and a retention locator.

The first alpha transports bounded inline canonical owner bytes only. It defines
no retained-reference transport.

## `projectkoios.workflow_sdk.firing`

### `WorkflowFiringBounds`

Frozen and slotted fields:

- `maximum_input_count: int`;
- `maximum_output_count: int`;
- `maximum_evidence_count: int`;
- `maximum_input_bytes: int`;
- `maximum_output_bytes: int`;
- `maximum_total_bytes: int`; and
- `maximum_reason_count: int`.

Every value is an exact nonnegative built-in integer within SDK hard limits.

### `WorkflowFirerDescriptor`

Frozen and slotted fields:

- `identity: WorkflowFirerIdentity`;
- `implementation_identity: WorkflowFirerImplementationIdentity`;
- `input_contracts: tuple[WorkflowPayloadContract, ...]`;
- `output_contracts: tuple[WorkflowPayloadContract, ...]`;
- `evidence_contracts: tuple[WorkflowPayloadContract, ...]`;
- `bounds: WorkflowFiringBounds`; and
- `sdk_contract_version: str`.

The descriptor contains no Python class, callable, live firer, import path,
credential, storage locator, marking, or service object.

### `WorkflowOccurrenceContext`

Frozen and slotted fields:

- `definition_identity: WorkflowDefinitionIdentity`;
- `net_instance_identity: WorkflowNetInstanceIdentity`;
- `transition_identity: WorkflowTransitionIdentity`;
- `predecessor_marking_identity: WorkflowMarkingIdentity`;
- `predecessor_revision: int`;
- `selected_binding_sha256: str`;
- `occurrence_identity: WorkflowOccurrenceIdentity`;
- `attempt_identity: WorkflowAttemptIdentity`; and
- `attempt_ordinal: int`.

The context contains no mutable marking or owner payload.

### `WorkflowTransitionFirerBinding`

Frozen and slotted fields:

- `identity: WorkflowTransitionBindingIdentity`;
- `definition_identity: WorkflowDefinitionIdentity`;
- `transition_identity: WorkflowTransitionIdentity`;
- `firer_identity: WorkflowFirerIdentity`;
- `input_roles: tuple[str, ...]`;
- `output_roles: tuple[str, ...]`; and
- `binding_version: str`.

The binding contains immutable identities and role names only; it never retains
a live firer or consumer object.

### `WorkflowFiringRequest`

Frozen and slotted fields:

- `identity: WorkflowFiringRequestIdentity`;
- `context: WorkflowOccurrenceContext`;
- `binding_identity: WorkflowTransitionBindingIdentity`;
- `firer_identity: WorkflowFirerIdentity`;
- `inputs: tuple[WorkflowInlinePayload, ...]`; and
- `sdk_contract_version: str`.

The request identity binds the context, binding, firer, ordered input metadata
and digests, and SDK contract version under the accepted identity profile.

### Closed result base and variants

`WorkflowFiringResult` is a nominal abstract base with no public constructor
state. The only admitted exact result classes are:

#### `WorkflowFiringSucceeded`

- `identity: WorkflowFiringResultIdentity`;
- `request_identity: WorkflowFiringRequestIdentity`;
- `occurrence_identity: WorkflowOccurrenceIdentity`;
- `attempt_identity: WorkflowAttemptIdentity`;
- `firer_identity: WorkflowFirerIdentity`;
- `outputs: tuple[WorkflowInlinePayload, ...]`;
- `evidence: tuple[WorkflowInlinePayload, ...]`; and
- `sdk_contract_version: str`.

#### `WorkflowFiringRejected`

- `identity: WorkflowFiringResultIdentity`;
- `request_identity: WorkflowFiringRequestIdentity`;
- `occurrence_identity: WorkflowOccurrenceIdentity`;
- `attempt_identity: WorkflowAttemptIdentity`;
- `firer_identity: WorkflowFirerIdentity`;
- `reason_codes: tuple[str, ...]`;
- `evidence: tuple[WorkflowInlinePayload, ...]`; and
- `sdk_contract_version: str`.

#### `WorkflowFiringFailed`

- `identity: WorkflowFiringResultIdentity`;
- `request_identity: WorkflowFiringRequestIdentity`;
- `occurrence_identity: WorkflowOccurrenceIdentity`;
- `attempt_identity: WorkflowAttemptIdentity`;
- `firer_identity: WorkflowFirerIdentity`;
- `failure_codes: tuple[str, ...]`;
- `evidence: tuple[WorkflowInlinePayload, ...]`; and
- `sdk_contract_version: str`.

The worker accepts these exact classes only. There is no ambiguous result in the
pure alpha because the firer cannot enter an external effect.

### `Firer`

`Firer` is a nominal abstract base class with:

- an abstract read-only `descriptor` property returning
  `WorkflowFirerDescriptor`;
- a concrete `fire(*, request: WorkflowFiringRequest) -> WorkflowFiringResult`
  template method; and
- an abstract `_fire(*, request: WorkflowFiringRequest) -> WorkflowFiringResult`
  implementation hook.

`fire()` validates the exact request type, descriptor type and identity,
contracts, bounds, exact result variant, and complete request/result
correlation before returning. `Firer.__init_subclass__()` rejects a subclass
that replaces `fire()`, making the validated template method non-overridable at
runtime. Consumer-owned integration ABCs extend `Firer` and encapsulate their
owner-specific request and result operations behind `_fire()`.

## `projectkoios.workflow_sdk.integration`

### `WorkflowIntegrationManifest`

Frozen and slotted fields:

- `identity: WorkflowIntegrationManifestIdentity`;
- `integration_identity: WorkflowIntegrationIdentity`;
- `package_name: str`;
- `package_version: str`;
- `distribution_sha256: str`;
- `sdk_contract_version: str`; and
- `firer_descriptors: tuple[WorkflowFirerDescriptor, ...]`.

### `WorkflowIntegrationManifestProvider`

Nominal abstract base class with one abstract, side-effect-free
`manifest() -> WorkflowIntegrationManifest` method.

### `WorkflowWorkerIntegration`

Nominal abstract base class with:

- an abstract read-only `manifest_identity` property returning
  `WorkflowIntegrationManifestIdentity`; and
- an abstract `firers() -> tuple[Firer, ...]` method.

The worker host validates that every returned object is a concrete `Firer`,
descriptor identities are unique, live descriptors exactly match the retained
manifest, and no advertised firer is missing or unadvertised firer is present.

## Alpha exclusions

The public inventory contains no types for:

- prepare, stage, start, observe, reconcile, cancel, or collect;
- claims, leases, dispatch intent, authority grants, or start keys;
- retention references or private operational locators;
- schedulers, worker daemons, registry databases, or service clients;
- mutable markings;
- `AbstractTask`;
- generic class registries;
- class-object dispatch; or
- consumer-domain identities and scientific policy.
