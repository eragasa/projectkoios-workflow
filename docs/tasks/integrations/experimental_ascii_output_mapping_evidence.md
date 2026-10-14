# Experimental ASCII owner-output mapping evidence

## Scope

This record covers one private Workflow service candidate that maps a validated,
path-free canonical-ASCII owner logical identity to one explicitly declared
`STRING` external variable in the current non-authoritative CPN shadow kernel.
It does not claim implementation or conformance for the proposed canonical CPN
payload and hierarchical binding contract set.

The candidate performs no owner-domain import or document parsing, artifact
resolution, current-marking read, reservation, persistence, CPN firing, effect,
or scientific acceptance.

## Implementation

The candidate is implemented by:

- `projectkoios.workflow.actions.ExperimentalWorkflowAsciiOutputMappingDescriptor`;
- `projectkoios.workflow.actions.ExperimentalWorkflowAsciiOutputMapper`; and
- `projectkoios.workflow.actions.ExperimentalWorkflowMappedActionResult`.

The content-identified descriptor closes the exact canonical SDK transition
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
Workflow repository: 300 passed
standalone SDK: 13 passed
focused mapping suite: 16 passed
Ruff: passed
Ruff format for changed Python files: passed
strict mypy: success for 35 source files
git diff --check: passed
architecture documentation: included in repository result
```

Focused adversarial coverage includes changed mapping content, stale predecessor
revision, changed selected-binding digest, wrong result correlation, wrong output
role or codec, missing or reordered evidence, malformed/non-ASCII/whitespace or
path-shaped identities, oversize identity, substituted payload digest,
unregistered external variable, and non-success result variants.

Source SHA-256 values:

- `actions/__init__.py`:
  `2b20a75710bfdb6d17a3ca18dc77b494bd9543afe175e825748e99d6e9afc66f`;
- `actions/_mapper.py`:
  `effb84e6e37329b1f1e45c65eb16080a54b2ccb03090c288cd437598ffb72755`;
- `actions/_models.py`:
  `65720374b80233f1834e6781ac293e54da381bdd10f7155b5947747405fc4e1d`;
- `actions/_validation.py`:
  `9f003239096c7bacd5d2b5ee201fe189fa1dad24949bfefb88bb6f7589fd7f2d`;
- `actions/mapping.py` public re-export:
  `efce40a64c6727f504a19d8b01b84bebe092067cf3604390ac387de39128d066`;
- focused test:
  `e7d4ab71f87bbf7daae0391ae8880f6aab287dfacb2e79d56b1057c8d369440f`.

## Reproducible wheel and isolated cross-wheel result

Two builds with `SOURCE_DATE_EPOCH=315532800` produced the same Workflow wheel:

- `projectkoios_workflow-0.0.0-py3-none-any.whl`;
- SHA-256
  `9f822ec654293f616898d7d49f7849f581f3bda34c51983da789a45af7f1049c`.

A fresh Python 3.14 environment installed that wheel with:

- Workflow SDK wheel SHA-256
  `925f6974c49c8935ebf2f002b18c86d29375e1b11c3ffc17a29d305fb8095ff4`;
- Simulations pilot wheel SHA-256
  `eea5dfdd8095d68a76b51960475b9869d25eb4f34ba467a5fd7c0c4f8abbef7d`.

All 24 installed packages passed dependency checking. An isolated invocation
called the Simulations owner `Firer.fire(...)`, passed its exact success to the
Workflow mapper, and produced:

- SDK request identity
  `d658a46ce184a34a33de5c2d83533f8f6330284b45178e3dad8c1e639f79c879`;
- SDK result identity
  `12270f112d303bca713c22b8ee5d015d8d120e39276623fc681782befbeee3fa`;
- mapping identity
  `2e0efdea9dd5c077d68b9a189283edee7b98fcb6c466161524dddedd867a1139`;
- mapped-result identity
  `b0916b4cd3310d6fdd416cdbc9ade73cd97dfc9973ba386323385fee7cbf9832`;
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

The candidate mapping descriptor is not yet part of a complete
`WorkflowExecutionPlan` or retained `WorkflowExecutionBindings`. The runtime
must still prove authoritative plan closure, current predecessor
reservation/revalidation, output-color compatibility, pure CPN firing, atomic
successor/history/evidence retention, and replay before the vertical slice can
complete.
