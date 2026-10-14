# `TransitionActionBinding`

## Responsibility

`TransitionActionBinding` binds one exact action descriptor to one compiled CPN
transition mapping. It constructs the owner request from a selected binding and
purely maps an admitted owner result into identified external variables plus
separately retained evidence.

The mapping must distinguish owner logical state from transport integrity. When
an owner defines a retention-independent logical result identity, that opaque
identity is the external CPN value; the SHA-256 of SDK payload bytes remains
exact-byte evidence and must not silently replace the owner identity.

For the QE SCF artifact-set direction, `artifact_set_identity` is the future
bounded Simulations-owned canonical ASCII output mapped to a CPN string
variable. The existing canonical `artifact_set` document is supporting SDK
evidence with its own payload digest. Workflow does not import Simulations
classes or parse the artifact-set JSON to derive the identity.

This component owns deterministic data adaptation and correlation only. It does
not select transitions, reserve tokens, admit a stale result, claim work,
authorize effects, choose providers, mutate markings, or fire the net. The
current `0.1.0a1` public inventory does not yet expose the complete mapping
contract described here.
