# `projectkoios.workflow.petrinet.colored.closure`

## Purpose

Execution-closure ownership namespace.

## Coordination boundary

This node coordinates `validation` and declares no directly declared classes. It selects typed
collaborators and preserves dependency direction. It does not resolve payload
bodies, invoke providers, access persistence, or grant execution authority.

## Composition strategy

Composition uses immutable values and identity-bearing operations. Child modules
own their local validation, representation, mapping, linking, or CPN semantics.
This level must not copy domain topology or merge schema admission,
authorization, firing, numerical verification, and scientific validation.

## Source

The production owner is `src/python/projectkoios/workflow/petrinet/colored/closure/__init__.py`. The companion implementation and
schematics documents record dependency rules and composition flow.
