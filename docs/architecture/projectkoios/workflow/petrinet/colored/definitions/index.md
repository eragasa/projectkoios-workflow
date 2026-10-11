# `projectkoios.workflow.petrinet.colored.definitions`

## Purpose

Immutable generic colored-Petri-net graph definitions. Definitions compose nominal colors, places, transitions, arcs, closed guards, and inscriptions without embedding a marking, Workflow payload policy, effects, persistence, or a wire version. Intrinsic collection identity and total-priority invariants are enforced here; graph references, admitted values, variable completeness, and definition/marking compatibility belong to the structural validator.

## Coordination boundary

This node coordinates no child package or module nodes and declares `CpnDefinitionIdentity`, `CpnPlaceIdentity`, `CpnTransitionIdentity`, `CpnSelectionPolicy`, `CpnArcIdentity`, `CpnColorDefinition`, `CpnPlaceDefinition`, `CpnTransitionDefinition`, `CpnArcDefinition`, `CpnDefinition`. It selects typed
collaborators and preserves dependency direction. It does not resolve payload
bodies, invoke providers, access persistence, or grant execution authority.

## Composition strategy

Composition uses immutable values and identity-bearing operations. Child modules
own their local validation, representation, mapping, linking, or CPN semantics.
This level must not copy domain topology or merge schema admission,
authorization, firing, numerical verification, and scientific validation.

## Source

The production owner is `src/python/projectkoios/workflow/petrinet/colored/definitions.py`. The companion implementation and
schematics documents record dependency rules and composition flow.
