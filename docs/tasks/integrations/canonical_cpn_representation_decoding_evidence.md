# Experimental canonical CPN representation decoding evidence

## Scope

This record covers bounded canonical decoding for the already-selected v0 flat
CPN definition representation and a new v0 semantic-marking representation. It
provides reconstruction primitives for later retained-profile replay. It does
not persist marking bodies, add them to compact commit state, or claim complete
CPN-bindings replay.

## Implemented boundary

- `ExperimentalWorkflowCpnDefinitionDecoder` reconstructs every current
  shadow-CPN definition field from the exact retained canonical UTF-8 JSON
  representation selected by
  `projectkoios.workflow.experimental-cpn-definition-json:0`.
- Definition decoding uses closed object shapes, exact built-in JSON types,
  bounded collections and text, bounded guard depth, closed enum values,
  canonical decimal i64 strings, and canonical finite `float.hex()` values.
- Successful definition decoding must re-encode byte-for-byte. Unknown fields,
  whitespace variants, reordered semantic collections, malformed variants,
  unsupported schema identities, and noncanonical scalar forms fail closed.
- `ExperimentalWorkflowPureActionCpnPlan` now performs complete canonical decode
  and exact nominal-identity comparison when reconstructing retained definition
  bytes. Its identity domain and valid deterministic vectors are unchanged.
- `ExperimentalWorkflowCpnMarkingEncoder` and
  `ExperimentalWorkflowCpnMarkingDecoder` select
  `projectkoios.workflow.experimental-cpn-marking-json:0` and preserve the exact
  marking identity, definition identity, complete place multiset, anonymous
  multiplicity, optional token identities, color identities, and every closed
  value kind.
- Marking decoding has the same exact-byte re-encoding requirement and bounded,
  closed failure behavior. Representation decoding remains distinct from the
  retained execution-profile validators used by later semantic replay.
- No provenance-bound source under `projectkoios.workflow.petrinet.colored` was
  changed.

## Adversarial evidence

Focused tests prove:

- exact definition and marking encode/decode/re-encode round trips;
- decoded definitions and markings remain accepted by the installed structural
  validators when the originals were valid;
- marking round trips preserve all six closed value kinds, signed-i64 limits,
  finite negative zero, Unicode, ordered duplicate string-sequence entries,
  anonymous tokens, and identified tokens;
- unknown fields, unsupported profiles, noncanonical whitespace, unsupported
  enum values, and non-byte decoder inputs fail closed; and
- the existing definition representation and CPN-plan deterministic vectors do
  not change.

## Validation

Validation from the uncommitted candidate on Workflow revision `f7217e7`:

- full Workflow suite: `394 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `58` production source files;
- Ruff, changed-source formatting, architecture/documentation checks, runtime
  dependency boundary, shadow provenance, and `git diff --check`: passed;
- two Workflow wheels built with the same `SOURCE_DATE_EPOCH` were
  byte-identical, SHA-256
  `5f1244cbe7119559e5731ff71d6d90a9b4d1e93f9f5beea2b51cf8acac0ec078`;
- the clean Workflow wheel installed with the standalone SDK wheel and imported
  all four public definition/marking encoder and decoder classes successfully.

Artifact SHA-256 values:

- shared closed representation primitives:
  `b469de7f459560d5c3297a69a3741b9ed15bab0b3dac911548e50bc2553bce2a`;
- definition representation codec:
  `d228672277c058874f8daf1567f26c3c3d080ffe58b5c64d0c9224381053af3c`;
- marking representation codec:
  `70bc4c39701e8c38f0b04884fada33165cea3f937a43d3a2236f7bf9a6ad0c6d`;
- focused codec tests:
  `3816ad477a44901bb2da6dcb23a4c99bfcdddcf08eb10b94758f6aeacd47bfa6`.

The pre-existing canonical definition digest and CPN-plan identity remain,
respectively,
`1344efeb8246cdef7d0bf720dd1ac06f08663ff9ca95bc93d88fe380a0d42234`
and
`ccfe9ca78f04da9167ef8237d81ccf048d1f09cf6765b8b8210ca7774f16b982`.
The canonical fixture marking representation SHA-256 is
`93b117ab8a206d638e9138a9f3862e759495404b945d1650853ae45e5a19139b`.

## Status and remaining gaps

These codecs are candidate reconstruction primitives only. A later bounded
[in-memory CPN refiring candidate](pure_action_cpn_refiring_evidence.md) now
combines them with selected-binding, external-output, retained-profile,
pure-refiring, result-identity, and successor comparison evidence. Complete
committed replay still requires durable atomic transcript linkage and complete
runtime safety-state reconstruction.

Compact commit events continue to retain identities and admitted evidence
references only. They do not embed definitions, marking bodies, owner payloads,
or private locators. A later history/plan retention boundary must reference or
retain the canonical CPN representations without expanding compact commit
privacy scope.
