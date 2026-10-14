# Experimental selected-binding request and ASCII output mapping evidence

## Scope

This record covers private Workflow service candidates that canonically encode
one exact ordered selected shadow-CPN binding, derive its digest, construct the
correlated SDK request, and map a validated path-free canonical-ASCII owner
logical identity to one explicitly declared `STRING` external variable. It does
not claim implementation or conformance for the proposed canonical CPN payload
and hierarchical binding contract set.

The candidate performs no owner-domain import or document parsing, artifact
resolution, current-marking read, reservation, persistence, CPN firing, effect,
or scientific acceptance.

## Implementation

The candidates are implemented by:

- `projectkoios.workflow.actions.ExperimentalWorkflowSelectedBindingEncoder`;
- `projectkoios.workflow.actions.ExperimentalWorkflowFiringRequestCoordinates`;
- `projectkoios.workflow.actions.ExperimentalWorkflowFiringRequestFactory`;
- `projectkoios.workflow.actions.ExperimentalWorkflowAsciiOutputMappingDescriptor`;
- `projectkoios.workflow.actions.ExperimentalWorkflowAsciiOutputMapper`; and
- `projectkoios.workflow.actions.ExperimentalWorkflowMappedActionResult`.

The selected-binding encoder preserves assignment order and closed CPN value
kinds in bounded canonical JSON, including decimal-string integers and
hexadecimal finite reals. The request factory derives the selected-binding
SHA-256 itself, validates exact descriptors, roles, inputs, bounds, transition,
and coordinates, and requires an exact SDK codec round trip. It has no argument
through which a caller can claim the selected-binding digest.

The content-identified mapping descriptor closes the exact canonical SDK transition
binding and firer descriptor, mapping version, decoder profile, output role,
external variable identity, and `STRING` value kind. The mapper requires exact
retained occurrence context, request/result correlation, canonical SDK round
trips, ordered payload-contract metadata, counts, bounds, payload digests,
evidence order, and canonical path-free ASCII before constructing a candidate
external binding.

The mapped result retains the exact mapping descriptor, SDK request and result
identities, source output, ordered evidence, external binding, and a derived
content identity. The owner identity string, source-output byte digest, and
evidence byte digest remain distinct.

## Software verification

Final local verification:

```text
Workflow repository: 308 passed
standalone SDK: 13 passed
focused request-and-mapping suite: 24 passed
Ruff: passed
Ruff format for changed Python files: passed
strict mypy: success for 37 source files
git diff --check: passed
architecture documentation: included in repository result
```

Focused adversarial coverage includes reordered selected assignments, changed
value kind or value, wrong selected transition, oversized selected values or
identities, wrong input role, codec, or bound, changed predecessor coordinates,
changed mapping content, stale predecessor revision or selected-binding digest,
wrong result correlation, wrong output role or codec, missing or reordered
evidence, malformed/non-ASCII/whitespace or path-shaped identities, oversize
identity, substituted payload digest, unregistered external variable, and
non-success result variants.

Source SHA-256 values:

- `actions/__init__.py`:
  `cfd7c036f97402971f0cfc8d6980568b30c7815c789f67d402d9ffcc9236e8db`;
- `actions/_binding.py`:
  `12c204893ff8ddbd383d7848c834af50862e3163384c5a425c49a05f2f92ab91`;
- `actions/_mapper.py`:
  `effb84e6e37329b1f1e45c65eb16080a54b2ccb03090c288cd437598ffb72755`;
- `actions/_models.py`:
  `65720374b80233f1834e6781ac293e54da381bdd10f7155b5947747405fc4e1d`;
- `actions/_request.py`:
  `87c4b7b581cc0e0253387a7512935257fdb25eccc4f3f09138b2dcea3e2bbd94`;
- `actions/_validation.py`:
  `9f003239096c7bacd5d2b5ee201fe189fa1dad24949bfefb88bb6f7589fd7f2d`;
- `actions/mapping.py` public re-export:
  `af97c34cda8b50f6bb205881aeeb797f6eeb7ae4bb187e01d0fd0c2236d971ed`;
- focused mapper test:
  `e7d4ab71f87bbf7daae0391ae8880f6aab287dfacb2e79d56b1057c8d369440f`;
- focused request-factory test:
  `61228464bd9f9086b0203526a537309165c00a942fe0df85fb23ea46fa467aa7`.

## Reproducible wheel and isolated cross-wheel result

Two builds with `SOURCE_DATE_EPOCH=315532800` produced the same Workflow wheel:

- `projectkoios_workflow-0.0.0-py3-none-any.whl`;
- SHA-256
  `381a43d08af154eec5f07348c25306d2dbb89e00270eebefabde98ef8a1cfab4`.

A fresh Python 3.14 environment installed that wheel with:

- Workflow SDK wheel SHA-256
  `925f6974c49c8935ebf2f002b18c86d29375e1b11c3ffc17a29d305fb8095ff4`;
- Simulations pilot wheel SHA-256
  `eea5dfdd8095d68a76b51960475b9869d25eb4f34ba467a5fd7c0c4f8abbef7d`.

All 24 installed packages passed dependency checking. An isolated invocation
constructed the SDK request from an exact empty selected binding, called the
Simulations owner `Firer.fire(...)`, passed its exact success to the Workflow
mapper, and produced:

- derived selected-binding SHA-256
  `18dd1e1133f21342ad8e8af0c887b29bd5f889f06098017214865e297284bea9`;
- SDK request identity
  `3ac7ecbe64517ab994f783f2ce7b1c850d13a7b9feaf06832abe14b3eee628f9`;
- SDK result identity
  `e03bedf7e0a6b4d1e48bd4d11481e885920f1f215b335439fa43b59df5e0b499`;
- mapping identity
  `2e0efdea9dd5c077d68b9a189283edee7b98fcb6c466161524dddedd867a1139`;
- mapped-result identity
  `d4e72689e2c771850c952c6963def8cfb9b98ffe448658e1a41690fe56477dd5`;
- external variable `artifact_set_identity`, value kind `string`;
- owner logical value
  `projectkoios.integrations.quantumespresso.qe-pw-scf-saved-state-artifact-set-semantic-identity:1:97a9d2a3557ed03503187e9bc067e0143624995a6a203918eef0df44ac99e0bc`;
- source-output payload SHA-256
  `1ae6ad5d2d0b0e2748f6bcf6ee2f3114918bdda55a5561ed4a06b960e75d59e0`;
- retained artifact-set evidence SHA-256
  `00589cf4e745ba9d23908f47f109874858db0d275d2cec490205c1f624136842`.

The imported mapping module came from the isolated installed Workflow wheel,
not the source worktree.

## Remaining gate

The selected-binding representation profile and candidate mapping descriptor
are not yet part of a complete `WorkflowExecutionPlan` or retained
`WorkflowExecutionBindings`. The runtime must still prove authoritative plan
closure, current predecessor reservation/revalidation, output-color
compatibility, pure CPN firing, atomic successor/history/evidence retention, and
replay before the vertical slice can complete.
