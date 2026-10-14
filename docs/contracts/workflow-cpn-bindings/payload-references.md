# Content-addressed domain payloads

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Content-addressed domain payloads

## `WorkflowDomainPayloadReference`

`WorkflowDomainPayloadReference` is the complete generic reference to one
immutable owner payload. To preserve the selected managed-project profile, it
MUST contain exactly these six fields and no generic envelope fields:

| Field | Requirement |
|---|---|
| `payload_identity` | Bounded owner-defined nominal identity of the typed value |
| `schema_identity` | Exact owner schema family and major version |
| `media_type` | Bounded registered JSON media type |
| `sha256` | 64 lowercase hexadecimal digits over the exact payload bytes |
| `byte_size` | Positive signed 64-bit integer |
| `artifact_identity` | Opaque immutable artifact-store identity |

Owner, codec, and contract-version identities belong to the compiled
`WorkflowPayloadColorBinding`, not this reference. The reference MUST NOT
contain payload bytes, a decoded mapping, credentials, private source text,
executable code, a mutable store handle, or a filesystem path.

The `WorkflowDomainPayloadReferenceIdentity` MUST be derived as:

```text
projectkoios.workflow.payload-reference:1:<sha256(canonical-reference-bytes)>
```

The identity is not embedded in the reference document and therefore introduces
no self-reference. `sha256` identifies the owner payload bytes;
`WorkflowDomainPayloadReferenceIdentity` identifies the complete reference
record. They MUST remain distinct.

SHA-256 establishes byte correlation only. It does not establish producer
authenticity, chronology, semantic validity, authorization, scientific
acceptance, or publication status.

## Identity and text bounds

Payload, schema, and artifact identities MUST be nonempty bounded ASCII
strings, exclude controls, and contain at most 512 bytes. The media type MUST
satisfy its registered JSON or vendor-tree grammar and the same size/control
bounds; its required `/` separator is not path syntax. The reference document
MUST contain at most 4096 bytes. `byte_size` MUST be greater than zero and no
greater than the owner schema's registered limit.

An artifact identity is an opaque locator under an artifact-owner contract. It
MUST NOT be a path beginning with `/`, `~/`, `\\`, `file:`, or a drive-letter
prefix. Resolving it to a machine locator belongs to an isolated resolver or
worker, never to the CPN kernel.

## Canonical reference JSON

The reference document MUST use this private canonical JSON profile:

- one top-level JSON object;
- UTF-8 without a byte-order mark;
- no leading or trailing bytes and no trailing newline;
- the exact closed field set above;
- object keys sorted lexically;
- compact `,` and `:` separators;
- non-ASCII characters emitted directly rather than ASCII-escaped;
- strings, signed 64-bit integers, exact Booleans, `null`, arrays, and objects
  only; and
- no binary64 JSON numbers, decimal extensions, `NaN`, or infinities.

The reference encoding MUST be byte-equivalent to the applicable value passed
to:

```python
json.dumps(
    value,
    ensure_ascii=False,
    allow_nan=False,
    separators=(",", ":"),
    sort_keys=True,
).encode("utf-8")
```

A structural reference decoder MUST reject duplicate keys, unknown keys,
missing keys, invalid UTF-8, unsupported reference-profile versions, invalid
field types, noncanonical bytes, over-limit content, inconsistent field values,
and a claimed reference identity that differs from the canonical reference-byte
digest. After typed construction, it MUST re-encode and require byte-for-byte
equality.

Digest and byte-size agreement with the owner payload can be checked only when
those payload bytes are supplied. Full reference validation MUST require exact
`byte_size` and SHA-256 agreement before owner decoding or token admission.

This profile is a private candidate boundary, not a public compatibility
promise.

## Owner payload bytes

The payload itself remains an owner artifact. The exact codec identity bound to
`schema_identity` in the execution plan determines canonical byte and typed
decoding rules. A codec claiming
`projectkoios.workflow.canonical-json-control:1` MUST apply the same JSON rules
above and MUST restrict control/provenance values to `null`, exact Booleans,
strings, signed 64-bit integers, arrays, and objects.

Scientific binary64 arrays, matrices, native files, and large manifests MUST
remain in owner formats with explicit codecs and artifact references. They MUST
NOT acquire an implicit JSON-number convention through this contract.

## `WorkflowDomainPayloadCodec`

A registered owner codec MUST provide the conceptual pure operations:

```text
encode_canonical(typed_value)
  -> payload_bytes + WorkflowDomainPayloadEncodingMetadata
assemble_reference(payload_bytes, encoding_metadata, artifact_identity)
  -> WorkflowDomainPayloadReference | closed_failure
decode_canonical(payload_bytes, reference)
  -> typed_value | closed_failure
```

`WorkflowDomainPayloadEncodingMetadata` contains the owner-derived
`payload_identity`, `schema_identity`, and `media_type`; it contains no artifact
identity. `assemble_reference` MUST compute `sha256` and `byte_size` from the
exact supplied bytes and combine them with the immutable store-provided
`artifact_identity`. It MUST NOT accept caller-claimed digest or size values.

Artifact retention is an outer effect owned by the artifact boundary:

1. the pure codec produces bytes and encoding metadata;
2. an authorized artifact operation durably retains the exact bytes and returns
   an immutable `artifact_identity`; and
3. the pure assembler constructs and validates the six-field reference.

The codec and assembler MUST:

- consume and produce immutable owner-defined typed values;
- avoid `Any`, raw mappings, and `object` as unspecified public boundaries;
- perform no filesystem, network, database, clock, random, authority, or
  calculator operation;
- strictly validate schema version, collection bounds, nominal identities,
  numeric types, and cross-field invariants;
- reject Boolean-as-number and numeric-string substitutions unless the owner
  schema explicitly defines a string representation; and
- return a closed typed failure rather than repairing input.

Generic Workflow validates and retains the reference. A runtime admission,
mapping, or replay-preverification adapter MAY invoke only the exact registered
owner codec and assembler. Generic Workflow MUST NOT fabricate an artifact
identity, interpret the owner payload's scientific or provider-specific fields,
or let the CPN kernel invoke a codec, assembler, or artifact store.
