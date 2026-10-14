# Workflow SDK `0.1.0a1` canonical serialization

## Status

The Project Koios operator authorized this canonical encoding for the first
pure-firing SDK alpha. The standalone package now implements it and records
conformance evidence in the SDK readiness task. This encoding does not define
transport, retention, effect lifecycle, or a compatibility promise beyond the
exact alpha version.

## Public module

`projectkoios.workflow_sdk.serialization` exports these concrete,
non-subclassable codecs:

- `WorkflowFirerDescriptorJsonCodec`;
- `WorkflowTransitionFirerBindingJsonCodec`;
- `WorkflowFiringRequestJsonCodec`;
- `WorkflowFiringResultJsonCodec`; and
- `WorkflowIntegrationManifestJsonCodec`.

The alpha defines no generic codec registry, runtime class-object dispatch, or
universal public codec base.

## Canonical JSON

Every codec emits one deterministic UTF-8 JSON object using the equivalent of:

```python
json.dumps(
    document,
    ensure_ascii=True,
    allow_nan=False,
    separators=(",", ":"),
    sort_keys=True,
).encode("utf-8")
```

A canonical document:

- has one object at its root;
- uses exact closed keys;
- includes `schema_identity` and `sdk_contract_version`;
- contains no floating-point values;
- admits exact JSON integers while rejecting Boolean-as-integer values;
- preserves semantically ordered arrays;
- canonically sorts set-like collections;
- rejects duplicates where uniqueness is required;
- contains no unknown or missing fields; and
- contains no UTF-8 BOM, leading whitespace, trailing whitespace, or trailing
  bytes.

## Inline payload bytes

`WorkflowInlinePayload.payload` is represented as padded standard Base64:

```python
base64.b64encode(payload).decode("ascii")
```

Decoding uses strict validation:

```python
base64.b64decode(value, validate=True)
```

The decoder re-encodes the decoded bytes and requires exact equality with the
supplied Base64 spelling. `payload_sha256` hashes the raw payload bytes, not the
Base64 spelling or containing SDK document.

## Schema and codec identities

| Record | Schema identity | Codec identity |
|---|---|---|
| Firer descriptor | `projectkoios.workflow-sdk.firer-descriptor:1` | `projectkoios.workflow-sdk.firer-descriptor-json:1` |
| Transition binding | `projectkoios.workflow-sdk.transition-firer-binding:1` | `projectkoios.workflow-sdk.transition-firer-binding-json:1` |
| Firing request | `projectkoios.workflow-sdk.firing-request:1` | `projectkoios.workflow-sdk.firing-request-json:1` |
| Firing result | `projectkoios.workflow-sdk.firing-result:1` | `projectkoios.workflow-sdk.firing-result-json:1` |
| Integration manifest | `projectkoios.workflow-sdk.integration-manifest:1` | `projectkoios.workflow-sdk.integration-manifest-json:1` |

The schema identity is stored inside the canonical document. Codec identity is
exact boundary metadata supplied by the invoking operation and is not duplicated
inside the document.

## Closed firing-result representation

`WorkflowFiringResultJsonCodec` admits exactly these `outcome` tags:

- `succeeded`;
- `rejected`; and
- `failed`.

Decoding uses explicit branches and exact SDK constructors. It never resolves a
Python class name or consults a registry. Each variant has its own exact allowed
field set; fields belonging to another variant are rejected instead of encoded
as `null`.

## Decoder sequence

Before returning a record, every decoder must:

1. reject empty or oversized input;
2. reject a UTF-8 BOM;
3. decode UTF-8 strictly;
4. detect duplicate JSON keys;
5. enforce maximum nesting depth;
6. check the exact root schema and SDK version;
7. reject unknown and missing keys;
8. check exact scalar and collection types;
9. validate Base64 and decoded-length bounds before constructing records;
10. construct exact nominal SDK records;
11. recompute all content identities, payload digests, and correlations; and
12. re-encode the reconstructed record and require byte-for-byte equality.

Malformed input fails closed and returns no partially trusted record.

## Identity and digest separation

The alpha distinguishes:

1. **Logical record identity** — derived from a versioned semantic projection
   that excludes the identity itself.
2. **Owner payload SHA-256** — derived from raw inline owner bytes.
3. **Encoded SDK document SHA-256** — derived from final canonical SDK JSON and
   carried by a later transport or retention boundary, not embedded in the
   encoded document.

The required construction order is:

```text
owner bytes
→ owner payload SHA-256
→ SDK record and logical identity
→ canonical SDK JSON
→ encoded-document SHA-256
→ transport
```

An SDK document must not directly or indirectly embed its own encoded-document
digest, transport-envelope identity, or retention locator.

## Canonical collection behavior

- Input and output contracts, roles, and payloads preserve descriptor-declared
  order.
- Integration-manifest firer descriptors are unique and sorted by firer identity.
- Reason and failure codes are unique and sorted lexically.
- Evidence preserves descriptor-declared role order.
- A decoded set-like collection that is not already canonical is rejected.

## Alpha exclusions

This encoding does not define:

- a network protocol or RPC framing;
- a retention-reference envelope;
- large or private payload transfer;
- credentials, authority grants, or sealed operational locators;
- effect lifecycle messages;
- schema negotiation or additive readers;
- compatibility with another SDK version; or
- serialization of live firers, callables, Python classes, markings, service
  clients, or persistence objects.
