# Workflow SDK `0.1.0a1` self-consumption evidence

## Scope

This record proves that the Workflow service distribution depends inward on the
standalone SDK and validates worker integrations using installed SDK types. It
does not accept an external owner dependency or complete the pure-firing
vertical slice.

## Dependency and implementation

`projectkoios-workflow` declares the exact runtime dependency
`projectkoios-workflow-sdk==0.1.0a1`. The service-owned
`projectkoios.workflow.worker.WorkflowWorkerIntegrationValidator` imports the
installed SDK surface and fails closed unless:

- the manifest is an exact `WorkflowIntegrationManifest`;
- the process-local integration nominally extends `WorkflowWorkerIntegration`;
- its manifest identity equals the retained manifest identity;
- it returns an exact tuple containing only concrete `Firer` objects;
- live firer descriptor identities are unique; and
- live descriptors exactly equal the complete retained manifest descriptor
  tuple.

The validator does not invoke a firer, retain live objects in a manifest, import
an owner package, or duplicate SDK records.

## Verification

The repository test suite passes with the installed SDK wheel:

```text
284 passed
```

The four worker-integration tests cover exact admission, stale manifest
identity rejection, descriptor-set mismatch, duplicate firer identity
rejection, non-`Firer` rejection, and non-subclassable validator enforcement.
Ruff and mypy also pass for the complete Workflow and SDK source trees.

A fresh Python 3.14 environment installed the SDK and Workflow wheels together
using `--no-deps`. An isolated interpreter verified the exact Workflow runtime
requirement and imported the Workflow validator through the installed SDK:

```text
isolated dual-wheel import: passed
runtime requirement: projectkoios-workflow-sdk==0.1.0a1
SDK version: 0.1.0a1
```

The evidence build produced
`projectkoios_workflow-0.0.0-py3-none-any.whl` with SHA-256
`57433c8ff413ec4f3cc18725df6b401b0e6742fc839ee92e0fed65faab778782`.
Two builds with `SOURCE_DATE_EPOCH=315532800` were byte-for-byte equal. The
wheel contains both
`projectkoios/workflow/worker/__init__.py` and
`projectkoios/workflow/worker/integration.py`.
