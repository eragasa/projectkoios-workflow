# `projectkoios.workflow.petrinet.colored.enablement`

## Purpose

Complete deterministic enablement for generic colored Petri nets. Enablement is a pure ActionObject operation over one exact definition and marking. Private occurrence coordinates enforce multiset capacity; public bindings contain only definition-declared variable/value assignments. The operation performs no selection, firing, Task invocation, external effect, persistence, authority decision, or scientific calculation.

## Coordination boundary

This node coordinates no child package or module nodes and declares `CpnEnablementResultIdentity`, `CpnOrderingPolicyIdentity`, `CpnTransitionEnablerIdentity`, `CpnEnablementFailureIdentity`, `CpnEnablementFailureCode`, `CpnEnablementFailure`, `CpnEnablementResult`, `CpnEnablementFailureState`, `CpnEnablementResultIdentityDeriverIdentity`, `CpnEnablementResultIdentityDerivationInput`, `CpnEnablementResultIdentityDeriver`, `CpnEnablementFailureBuildingInput`, `CpnEnablementFailureBuilderIdentity`, `CpnEnablementFailureBuilder`, `CpnEnabledBindingOrderingInput`, `CpnEnabledBindingOrderingResult`, `CpnEnabledBindingOrderingPolicy`, `CpnTransitionEnablementRequest`, `CpnTransitionEnabler`. It selects typed
collaborators and preserves dependency direction. It does not resolve payload
bodies, invoke providers, access persistence, or grant execution authority.

## Composition strategy

Composition uses immutable values and identity-bearing operations. Child modules
own their local validation, representation, mapping, linking, or CPN semantics.
This level must not copy domain topology or merge schema admission,
authorization, firing, numerical verification, and scientific validation.

## Source

The production owner is `src/python/projectkoios/workflow/petrinet/colored/enablement.py`. The companion implementation and
schematics documents record dependency rules and composition flow.
