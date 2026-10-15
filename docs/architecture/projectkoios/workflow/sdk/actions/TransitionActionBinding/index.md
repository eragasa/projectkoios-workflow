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

For the QE SCF artifact-set direction, `artifact_set_identity` is the bounded
Simulations-owned canonical ASCII output mapped to a CPN string variable. The
existing canonical `artifact_set` document is supporting SDK evidence with its
own payload digest. Workflow does not import Simulations classes or parse the
artifact-set JSON to derive the identity.

This component owns deterministic data adaptation and correlation only. It does
not select transitions, reserve tokens, revalidate a current predecessor, claim
work, authorize effects, choose providers, mutate markings, or fire the net.

`projectkoios.workflow.actions` now contains an explicitly experimental request
factory and result mapper for the current non-authoritative shadow kernel. A
Workflow-owned evidence record first requires an exact successful enablement and
selection pair, proves that the selected binding occurs in the enabled-binding
set, and binds the adapter-profile identity and canonical bytes. The factory
consumes that evidence and derives no binding claim from a bare caller-supplied
binding. An additional experimental input-mapping descriptor selects an opaque
retained-source kind and representation profile for each ordered SDK input role.
The runtime input-admission candidate correlates those source-evidence records
before constructing the SDK request; durable source authority remains separate.
The mapper closes the same exact SDK transition binding and firer
descriptor, validates a retained occurrence context and correlated success, and
constructs one declared external `STRING` binding. These are private Workflow
service candidates, not part of the standalone SDK `0.1.0a1` inventory and not
an implementation claim for the proposed full CPN-bindings contract.
