# Workflow SDK `0.1.0a1` standalone implementation evidence

## Scope

This record covers the standalone SDK build root and package only. It does not
accept Workflow service self-consumption, an external owner dependency, the pure
firing vertical slice, release, or production use.

## Built artifact

- Distribution: `projectkoios-workflow-sdk`
- Version: `0.1.0a1`
- Wheel: `projectkoios_workflow_sdk-0.1.0a1-py3-none-any.whl`
- SHA-256: `925f6974c49c8935ebf2f002b18c86d29375e1b11c3ffc17a29d305fb8095ff4`
- Build command: `SOURCE_DATE_EPOCH=315532800 .venv/bin/python -m pip wheel ./sdk --no-deps --wheel-dir sdk/dist`
- Runtime requirements: none; all recorded requirements are guarded by the
  optional `dev` extra.

Two clean builds using the recorded source-date epoch were byte-for-byte equal.
The wheel contains:

```text
projectkoios/workflow_sdk/__init__.py
projectkoios/workflow_sdk/_validation.py
projectkoios/workflow_sdk/firing.py
projectkoios/workflow_sdk/identities.py
projectkoios/workflow_sdk/integration.py
projectkoios/workflow_sdk/payloads.py
projectkoios/workflow_sdk/py.typed
projectkoios/workflow_sdk/serialization.py
projectkoios_workflow_sdk-0.1.0a1.dist-info/METADATA
projectkoios_workflow_sdk-0.1.0a1.dist-info/WHEEL
projectkoios_workflow_sdk-0.1.0a1.dist-info/top_level.txt
projectkoios_workflow_sdk-0.1.0a1.dist-info/RECORD
```

## Conformance results

The following commands passed on 2026-10-14:

```text
cd sdk && ../.venv/bin/ruff check .
All checks passed!

cd sdk && ../.venv/bin/ruff format --check .
9 files already formatted

cd sdk && ../.venv/bin/mypy src/python tests
Success: no issues found in 8 source files

cd sdk && PYTHONPATH=src/python ../.venv/bin/python -m pytest -q tests
13 passed
```

The tests retain evidence for nominal ABC enforcement, the non-overridable
`Firer.fire()` template, immutable records, exact result admission, stale
request/result correlation rejection, payload digest validation, canonical
round trips for all five public codecs, duplicate and unknown JSON key
rejection, noncanonical document and Base64 rejection, empty and oversized
document rejection, and bounded collection rejection.

## Isolated installation

A fresh Python 3.14 virtual environment installed the wheel with `--no-deps`.
An isolated interpreter (`python -I`) imported the package constants, `Firer`,
`WorkflowFiringResult`, and `WorkflowFiringResultJsonCodec`, verified version
`0.1.0a1`, and verified that the distribution has no unguarded runtime
requirements.

```text
isolated install: passed
version: 0.1.0a1
runtime requirements: none
```

## Alpha compatibility statement

The wheel metadata incorporates `sdk/README.md`, which states that every public
surface may change or be removed, consumers must pin the exact alpha version,
compatibility with another SDK version is not promised, and the package is not
for production, effects, authority or credential transfer, private or large
payload transfer, or replacement of authoritative CPN state and history.
