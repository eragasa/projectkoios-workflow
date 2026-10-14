# Workflow CPN SDK error handling

The SDK separates malformed calls from represented semantic failures. Consumers
must preserve that distinction. The machine-readable
[`operation-manifest.json`](operation-manifest.json) records every public enum
and its exact members; filter `public_types` for `kind == "enum"` rather than
copying or guessing failure-code strings.

## Construction and boundary errors

Exact record constructors reject invalid Python boundary values immediately:

- `TypeError` means the supplied runtime type is not the declared exact type.
- `ValueError` means the type is correct but an intrinsic invariant, bound,
  ordering rule, identity domain, or canonical representation is invalid.

These exceptions indicate an SDK caller or retained-data defect. They are not
workflow outcomes and must not be converted into scientific failure states.
Catch them only at an integration boundary where the exact rejected input and
operation identity can be retained.

## Validation findings

Validators return immutable result objects containing complete typed findings.
Inspect `is_valid` and then the closed finding-code enum. Do not stop at the
first finding or parse human-readable messages.

```python
result = validator.execute(request)
if not result.is_valid:
    for issue in result.issues:
        handle(issue.code, issue.path)
```

## Enablement, selection, and firing outcomes

Enablement, selection, and firing return represented result variants. Branch on
the declared outcome enum and then inspect the corresponding typed failure or
success fields. Never infer success from `None`, object truthiness, or the lack
of an exception.

A firing failure does not mutate the predecessor marking. A successful result
contains a separately identified successor marking and occurrence audit.

## Canonical transport rejection

Canonical decoders accept exact immutable bytes and retained correlation
objects. Malformed JSON, duplicate keys, unsupported numbers, noncanonical
ordering, identity mismatch, profile substitution, and replay mismatch are
boundary defects. Reject them; do not repair, normalize, or silently re-encode
untrusted input.

## Payload-reference outcomes

Payload-reference assembly returns either a reference or a typed assembly
failure. Verification returns a complete ordered tuple of verification issues.
A matching digest establishes only exact-byte correlation. It does not establish
artifact authority, codec correctness, payload semantics, authorization, or
scientific validity.

## Child-plan linking outcomes

Child-plan/export correlation returns exact mismatched field names. Static
reference validation returns typed self-reference, unreachable-reference, or
cycle findings. These concern immutable parent-plan to child-plan references,
not CPN transition cycles, retries, concurrency, or event history.

## Logging and durable evidence

Retain at least:

- action or codec semantic identity;
- request-owned definition, plan, or profile identity;
- content identity and byte digest where applicable;
- closed failure/finding code;
- canonical artifact identity or retained reference identity.

Do not log opaque provider payload bodies merely to diagnose Workflow-level
correlation failures.
