# `projectkoios.workflow.petrinet.colored.selection`

## Purpose

Deterministic and explicitly permitted directed binding selection. Selection consumes one complete identity-bound enablement result. It performs no firing, marking mutation, Task invocation, external effect, authority decision, persistence, fairness scheduling, or scientific calculation.

## Coordination boundary

This node coordinates no child package or module nodes and declares `CpnSelectionDirectiveIdentity`, `CpnSelectionResultIdentity`, `CpnBindingSelectorIdentity`, `CpnSelectionDirective`, `CpnSelectionOutcomeKind`, `CpnSelectionFailureCode`, `CpnSelectionResult`, `CpnBindingSelectionRequest`, `CpnBindingSelector`. It selects typed
collaborators and preserves dependency direction. It does not resolve payload
bodies, invoke providers, access persistence, or grant execution authority.

## Composition strategy

Composition uses immutable values and identity-bearing operations. Child modules
own their local validation, representation, mapping, linking, or CPN semantics.
This level must not copy domain topology or merge schema admission,
authorization, firing, numerical verification, and scientific validation.

## Source

The production owner is `src/python/projectkoios/workflow/petrinet/colored/selection.py`. The companion implementation and
schematics documents record dependency rules and composition flow.
