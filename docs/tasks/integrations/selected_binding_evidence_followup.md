# Selected-binding evidence follow-up

## Scope

This record covers the Workflow-owned evidence boundary added after the
experimental selected-binding request review. It prevents the request factory
from accepting a bare CPN binding while preserving the provenance-bound,
byte-identical shadow CPN source.

It does not establish a current reservation, input provenance, authoritative
execution-plan closure, persistence, CPN firing, or replay.

## Implementation

`ExperimentalWorkflowSelectedBindingEvidence` accepts one exact
`ColoredPetriNetEnablementResult` and one exact
`ColoredPetriNetSelectionResult`. Construction requires:

- successful enablement with a closed enabled-binding tuple;
- a selected outcome containing one binding;
- exact enablement-result and ordering-policy correlation;
- membership of the selected binding in the enabled-binding set;
- canonical selected-binding bytes derived by the existing Workflow adapter
  profile; and
- a derived content identity over the definition, predecessor marking,
  transition, enablement result, selection result, adapter profile, canonical
  byte length, and binding-byte SHA-256.

The firing-request factory now accepts this evidence instead of a bare binding.
It reconstructs the evidence, rejects substituted derived fields, and requires
the selected definition, transition, and predecessor marking to match the SDK
transition binding and request coordinates. The adapter-profile identity and
canonical bytes remain available for later plan and persistence work.

## Software verification

Final local verification:

```text
Workflow repository: 315 passed
standalone SDK: 13 passed
focused selected-binding request suite: 15 passed
Ruff: passed
Ruff format for changed Python files: passed
strict mypy: success for 38 source files
architecture documentation: passed
documentation links missing: 0
git diff --check: passed
shadow CPN provenance checks: passed
```

Focused adversarial coverage rejects a nonselected result, a selected binding
absent from enablement, a changed enablement-result link or ordering policy,
wrong definition, wrong transition, wrong predecessor marking, substituted
representation-profile identity, malformed profile/evidence identities, and the
previously covered
payload, bound, coordinate, and canonical-binding defects.

Source SHA-256 values:

- `actions/_selection.py`:
  `64be53e09daca757e55310fb8e9d13ed777a1edac847a6f2a6b40bc5a80a9340`;
- `actions/_request.py`:
  `fa881e8dda1bd7c97d79e8d5a2090e88993fa69667792fd9a6172c9c63c315f1`;
- focused request/evidence test:
  `c718b6eaaad702c401d32e3a40cd3e20c4dc5669be0019d7c53fd9fea5ac715b`.

## Reproducible wheel and isolated result

Two builds with `SOURCE_DATE_EPOCH=315532800` produced the same Workflow wheel:

- `projectkoios_workflow-0.0.0-py3-none-any.whl`;
- SHA-256
  `fec5d9e686959f8e6d38dfd73a215b62c37005941b92eff8494099021c5ef663`.

A fresh Python 3.14 isolated environment retained 24 dependency-compatible
packages, installed the new Workflow wheel, constructed selected-binding
evidence from an exact successful enablement/selection pair, constructed the
SDK request, invoked the Simulations owner firer, and mapped its success. It
produced:

- selected-binding evidence identity
  `dea72d1e4a0c5f07cc8e0ff8c9d7bedb7d6668bce9b37b3ef66a3a948f172723`;
- selected-binding profile identity
  `projectkoios.workflow.experimental-selected-binding-canonical-json:1`;
- selected-binding SHA-256
  `18dd1e1133f21342ad8e8af0c887b29bd5f889f06098017214865e297284bea9`;
- unchanged SDK request identity
  `3ac7ecbe64517ab994f783f2ce7b1c850d13a7b9feaf06832abe14b3eee628f9`;
- unchanged SDK result identity
  `e03bedf7e0a6b4d1e48bd4d11481e885920f1f215b335439fa43b59df5e0b499`;
- unchanged mapping identity
  `2e0efdea9dd5c077d68b9a189283edee7b98fcb6c466161524dddedd867a1139`;
- unchanged mapped-result identity
  `d4e72689e2c771850c952c6963def8cfb9b98ffe448658e1a41690fe56477dd5`.

The unchanged downstream identities demonstrate that the new evidence adds
structural selection correlation without altering the established canonical
binding bytes or SDK request semantics. Authoritative provenance still requires
retained-state reservation and revalidation.

## Remaining gate

Runtime coordinates and owner inputs remain independently supplied. The next
foundation must bind them to a current reservation and explicit input-source
mapping before the request can be treated as authoritative invocation evidence.
