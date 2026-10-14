# QE artifact-set Workflow SDK pilot evidence

## Scope

This record covers the Simulations-owned pure SDK boundary only. It does not
claim an isolated Workflow worker, an authoritative selected or reserved CPN
binding, external-output admission, predecessor revalidation, CPN firing,
retention, calculator execution, or scientific acceptance.

## Repositories and artifacts

- Workflow SDK source repository base:
  `projectkoios-workflow@63f127dd6922c16accb3dc857cfb2e28224a8958`, plus
  the authorized uncommitted SDK candidate recorded by its exact wheel.
- SDK wheel: `projectkoios_workflow_sdk-0.1.0a1-py3-none-any.whl`.
- SDK wheel SHA-256:
  `925f6974c49c8935ebf2f002b18c86d29375e1b11c3ffc17a29d305fb8095ff4`.
- Simulations worktree:
  `/Users/eugene/worktrees/projectkoios-simulations-qe-scf-workflow-sdk-pilot`.
- Simulations branch: `feature/qe-scf-workflow-sdk-pilot`.
- Simulations base and current uncommitted HEAD:
  `ff5f3dac431b3d56204248b64b9646a6f9cd0c8b`.
- Simulations wheel:
  `projectkoios_simulations-0.1.0.dev0-py3-none-any.whl`.
- Simulations wheel SHA-256:
  `eea5dfdd8095d68a76b51960475b9869d25eb4f34ba467a5fd7c0c4f8abbef7d`.

No commit or push occurred.

## Implemented owner boundary

The pilot pins `projectkoios-workflow-sdk==0.1.0a1` and adds:

- a strict Simulations-owned canonical projection-request codec;
- a nominal Simulations ABC extending the SDK `Firer`;
- a concrete wrapper around the unchanged
  `QeScfSavedStateArtifactSetProjector`;
- one immutable descriptor with input role `projection_request`, output role
  `artifact_set_identity`, and evidence role `artifact_set`;
- one explicitly nonproduction transition-binding fixture;
- a 4-MiB input/evidence bound and 256-byte identity-output bound;
- exact request/result correlation, including reconstruction of the returned
  owner result to re-run owner semantic-identity invariants;
- rejection of malformed input, private URI/path-shaped locators, mismatched
  metadata, firer identity, and noncanonical documents; and
- closed success, rejection, and known pure-failure behavior.

The integration emits the owner logical artifact-set identity as exact canonical
ASCII and retains the unchanged canonical artifact-set document as SDK evidence.
It does not transport the candidate fragment, whose owner codec is outside this
pilot. The identity codec uses:

- payload type
  `projectkoios.integrations.quantumespresso.qe-pw-scf-saved-state-artifact-set-identity`;
- schema
  `projectkoios.integrations.quantumespresso.qe-pw-scf-saved-state-artifact-set-identity:1`;
- codec
  `projectkoios.integrations.quantumespresso.qe-pw-scf-saved-state-artifact-set-identity-ascii:1`;
- representation `canonical-ascii:1`;
- media type
  `application/vnd.projectkoios.qe-pw-scf-saved-state-artifact-set-identity.v1+ascii`;
  and
- maximum encoded length 256 bytes, with no BOM, controls, DEL, whitespace,
  newline, framing, or trailing bytes.

## Verification

Independent Workflow-owner review initially found three blocking defects:
owner-result correlation was incomplete, URI-shaped private locators could
cross the inline boundary, and the fixture conflated two binding identities.
All three were corrected and the follow-up review outcome was
`NO_BLOCKING_FINDINGS` with no operator input required.

A second Workflow-owner follow-up review of the revised owner-output shape found
no retained findings. Its outcome was `NO_BLOCKING_FINDINGS`, its operator
request was `NONE`, and no additional Simulations change was required for the
pilot scope.

Final owner-reported results:

```text
692 passed, 7 skipped, 202 subtests passed
Ruff check: passed
Ruff format: passed
mypy: success for 220 source files
focused SDK/domain suite: 81 passed
git diff --check: passed
```

The Workflow-owner review independently repeated the focused 81-test suite,
Ruff, formatting, strict mypy, and diff validation successfully.

The protected existing owner sources remain byte-identical:

- `saved_state_artifact_set.py` SHA-256:
  `6e1ad5c573dff8c0304157c2ca5eff4d8d0819fbca3efee7ecace84c5226b5d6`;
- `saved_state_candidate.py` SHA-256:
  `d605a8fa30f9da3456a17777c02250eee3666e0b498bdab03a4d8657c5aea6b1`.

## Isolated cross-wheel result

A fresh Python 3.14 virtual environment installed the exact SDK and Simulations
wheels, passed dependency checking, and invoked
`QeScfSavedStateArtifactSetProjectorFirer.fire(...)` under `python -I`.
The invocation returned `WorkflowFiringSucceeded` with one
`artifact_set_identity` output and one `artifact_set` evidence payload.

Retained identities from that run:

- SDK request:
  `a8a1fc501f8b9dc813e46622b1f0a70b3f324be961a84aa630c93227964da21b`;
- SDK result:
  `9902a8b2703e359ffaf37c641294c54b0e1dff57ceb1fb9e93ec6bac90fafe40`;
- decoded owner identity:
  `projectkoios.integrations.quantumespresso.qe-pw-scf-saved-state-artifact-set-semantic-identity:1:97a9d2a3557ed03503187e9bc067e0143624995a6a203918eef0df44ac99e0bc`;
- identity output length 161 and payload SHA-256:
  `1ae6ad5d2d0b0e2748f6bcf6ee2f3114918bdda55a5561ed4a06b960e75d59e0`;
- artifact-set evidence length 1175 and payload SHA-256:
  `dd83315120295c7d47b6dde767a26d4531858c216d6419a2f9ca16b0a3c98fef`.

The output and evidence hashes are distinct. The decoded evidence contained four
artifact members. All 23 installed packages were compatible.

## Remaining Workflow gate

The revised owner boundary now supplies the selected long-term state shape:
canonical `artifact_set_identity` output plus the complete `artifact_set`
document as evidence. The payload digest continues to identify exact bytes only
and is not the owner logical identity.

Workflow does not yet implement the mapping from that opaque owner identity to
an identified CPN external-output binding. The pilot therefore remains
fail-closed after the correlated SDK result. Workflow must separately define and
validate the selected-binding digest, predecessor reservation/revalidation,
external-output mapping, atomic CPN firing retention, and replay evidence before
the pure vertical slice can complete.
