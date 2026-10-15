# Experimental pure-action plan-closure evidence

## Scope

This record covers the smallest Workflow-owned compilation candidates that
retain the selected-binding representation profile and owner-result mapping
through a plan-shaped semantic record and verify the plan-selected firer against
an exact SDK integration manifest.

The candidates are intentionally narrower than `WorkflowExecutionPlan` and
`WorkflowExecutionBindings`. They do not claim the proposed complete
CPN-bindings contract, canonical flat-definition closure, input-source mapping,
reservation, persistence, or replay.

## Implementation

`ExperimentalWorkflowPureActionExecutionPlan` is a frozen, slotted,
content-identified record containing:

- the exact selected-binding adapter-profile identity; and
- the exact `ExperimentalWorkflowAsciiOutputMappingDescriptor`.

The mapping descriptor transitively closes the SDK transition binding, firer
descriptor, output role, evidence contracts, decoder profile, target external
variable, value kind, and mapping version. Reconstructing the plan revalidates
the complete mapping descriptor and retains any bounded nominal selected-binding
profile without consulting the current encoder default. This keeps older plan
records representable; execution support remains a separate validation concern.

`ExperimentalWorkflowPureActionExecutionBindings` retains that exact plan
candidate and one canonical `WorkflowIntegrationManifest`. Linking requires the
manifest to contain exactly the firer descriptor already selected by the plan.
It cannot substitute another output mapping, descriptor implementation, or
selected-binding profile. No live `Firer`, worker, provider, environment, or
repository object enters either record.

## Software verification

Final local verification:

```text
Workflow repository: 320 passed
standalone SDK: 13 passed
focused plan/linking suite: 5 passed
Ruff: passed
Ruff format for changed Python files: passed
strict mypy: success for 40 source files
architecture documentation: passed
documentation links missing: 0
git diff --check: passed
shadow CPN provenance checks: passed
```

Focused coverage demonstrates deterministic plan and binding identities, plan
identity changes for mapping-version and selected-binding-profile changes,
deployment identity changes for manifest or retained-profile changes, rejection
of forged mapping identities, missing firers, changed firer implementations,
and forged nested plan identities.

Source SHA-256 values:

- `compilation/__init__.py`:
  `887544ca7cd8d45b4cfa5f4405f19d2d86309656934ac1f2535015be6396a0b8`;
- `compilation/pure_action.py`:
  `4b4f306ce31640c7ac27864f39df91637deabfb70fc062446ba43fa72a6e49ff`;
- focused plan/linking test:
  `7106037a16d62e510b9ff8e49dac6ac2b2d1dfbee5dc7f800962af419fcf5257`.

## Reproducible wheel and isolated result

Two builds with `SOURCE_DATE_EPOCH=315532800` produced the same Workflow wheel:

- `projectkoios_workflow-0.0.0-py3-none-any.whl`;
- SHA-256
  `e11000cf931f20549d111d73208fbace55eb43368d0d83126910d630d6da14d2`.

A Python 3.14 isolated environment with 24 dependency-compatible packages
installed the wheel, reconstructed the existing Simulations-backed request and
mapping path, created the bounded plan candidate, linked it to an exact
Simulations SDK integration manifest, invoked the owner firer, and mapped its
success. It produced:

- pure-action plan identity
  `fbe0465a5264dc02b23ba1d5dc860bfb7c4849caecdf1c37fe576e06cc468143`;
- pure-action execution-bindings identity
  `9627a3c1581d77d960f0774fbab04f892402fc3465238f608093375db81e5aed`;
- unchanged selected-binding evidence identity
  `dea72d1e4a0c5f07cc8e0ff8c9d7bedb7d6668bce9b37b3ef66a3a948f172723`;
- unchanged SDK request identity
  `3ac7ecbe64517ab994f783f2ce7b1c850d13a7b9feaf06832abe14b3eee628f9`;
- unchanged SDK result identity
  `e03bedf7e0a6b4d1e48bd4d11481e885920f1f215b335439fa43b59df5e0b499`;
- unchanged output-mapping identity
  `2e0efdea9dd5c077d68b9a189283edee7b98fcb6c466161524dddedd867a1139`;
- unchanged mapped-result identity
  `d4e72689e2c771850c952c6963def8cfb9b98ffe448658e1a41690fe56477dd5`.

## Remaining gate

A complete authoritative execution plan must still close the canonical flat CPN
definition, initial marking, input-source mapping, execution profiles, routes,
compiler evidence, and any nested or terminal semantics. Complete deployment
bindings must add exact worker/environment routing without introducing live
objects. Reservation and current-predecessor revalidation remain subsequent
runtime work.
