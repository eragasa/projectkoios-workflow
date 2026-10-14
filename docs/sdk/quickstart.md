# Workflow CPN SDK quick start

Status: release-candidate SDK surface for `projectkoios/workflow/v0.1`.

The SDK exposes immutable records and identity-bearing semantic actions. Package
initializers are namespace boundaries; import each type from the semantic owner
module listed in
[`operation-manifest.json`](operation-manifest.json). The manifest is generated
as an offline documentation/build artifact and checked exactly in CI. Every
entry declares its intended evaluation audiences and remains
`release-candidate`; `compatibility_commitment` is false until a provider trial
selects the demonstrated stable subset. The manifest is not a runtime
reflection, registration, or autodiscovery mechanism.

This SDK status stabilizes the documented direct-module imports for evaluation.
It does not authorize provider effects, consumer migration, scientific
acceptance, or release of a provider-owned workflow definition.

## Local installation

The package is not published yet. From a checked-out repository:

```console
uv sync --locked --all-extras
uv build --out-dir dist
uv venv /tmp/projectkoios-workflow-sdk --python 3.14 --clear
uv pip install --python /tmp/projectkoios-workflow-sdk/bin/python dist/*.whl
```

Python 3.14 or newer is required.

## Protocol used by every operation

1. Construct exact immutable owner records.
2. Construct the operation-specific request record.
3. Instantiate the stateless action.
4. Call its single `execute(request)` method.
5. Inspect the typed response, outcome, or findings.
6. Retain action and content identities with durable evidence.

Canonical codecs are the sole documented exception: they expose typed `encode`
and `decode` methods. Do not pass dictionaries, callbacks, provider objects, or
filesystem paths in place of the declared records.

## Executable examples

The examples are executed against a clean installed wheel in CI:

| Task | Example |
|---|---|
| Construct and validate a flat definition | [`examples/sdk/define_validate.py`](../../examples/sdk/define_validate.py) |
| Enable, deterministically select, and purely fire | [`examples/sdk/execute_firing.py`](../../examples/sdk/execute_firing.py) |
| Canonically encode and replay a firing result | [`examples/sdk/canonical_replay.py`](../../examples/sdk/canonical_replay.py) |
| Assemble, transport, and verify an opaque payload reference | [`examples/sdk/payload_reference.py`](../../examples/sdk/payload_reference.py) |
| Compile, export, correlate, and link a child plan | [`examples/sdk/child_plan_export.py`](../../examples/sdk/child_plan_export.py) |

Run them from the repository root:

```console
uv run python examples/sdk/define_validate.py
uv run python examples/sdk/execute_firing.py
uv run python examples/sdk/canonical_replay.py
uv run python examples/sdk/payload_reference.py
uv run python examples/sdk/child_plan_export.py
```

## LLM use

An LLM should read `operation-manifest.json` before writing integrations. For
each task, select an operation by its action name or semantic identity, import
it from the exact `module`, and construct the listed `request_types`. Never
invent an aggregate import from a package initializer.

Use the checked examples as generation patterns. Preserve complete owner
objects in requests and branch on closed enum outcomes or typed findings. Do
not infer success from truthiness, a missing exception, or a digest match.

“LLM use” here means reliable SDK discovery and code generation, not an
LLM-driven execution authority. Any future LLM execution adapter must remain
provider-neutral and retain the model/provider, exact prompt or template, tool
permissions, repository/branch/allowed paths, protected-action permissions,
input/output hashes, reviews, and human decisions.

## Boundary reminders

- Domain repositories own topology, payload schemas, mappings, codecs, and
  scientific policy.
- Workflow owns correlation, deterministic ordering, branching, persistence,
  replay, capability declarations, authorization gates, and failure routing.
- Workflow does not own projections, physical units, nondimensionalization,
  fitting, optimization, feasibility mathematics, provider behavior,
  scientific thresholds, or scientific dispositions.
- Providers declare capabilities, accept canonical requests, return correlated
  results, retain lineage, expose deterministic failures, and pass conformance
  tests.
- Workflow validates, links, persists metadata, and fires the generic CPN.
- Opaque provider payload bytes appear only at persistence or transport
  boundaries.
- SHA-256 provides exact-byte correlation, not authenticity or scientific
  validity.
- A child export references a separately owned child plan; parent workflows do
  not copy child topology.
- The static child-plan reference cycle restriction does not constrain cyclic
  CPN execution topology.

See [`error-handling.md`](error-handling.md) before consuming result objects.
Provider repositories use the separately scoped
[`provider-conformance.md`](provider-conformance.md) test protocol.
