# `projectkoios.workflow.petrinet.colored.values`

## Purpose

Immutable generic colored-Petri-net values and tokens. A :class:`CpnValue` is a finite, explicitly tagged value available to generic inscriptions and guards. A :class:`CpnToken` associates one such value with a color and, when individual correlation is required, a nominal token identity. Indistinguishable-token multiplicity belongs exclusively to the marking that contains tokens; it is not stored on a token. These records contain no Workflow, scientific-result, calculator, persistence, authority, or external-effect meaning. Construction tests are software verification and establish no numerical verification, scientific validation, or uncertainty quantification.

## Coordination boundary

This node coordinates no child package or module nodes and declares `CpnValueModelIdentity`, `CpnColorIdentity`, `CpnTokenIdentity`, `CpnValueKind`, `CpnValue`, `CpnControlRecordTypeIdentity`, `CpnControlRecordFieldIdentity`, `CpnControlRecordFieldDefinition`, `CpnControlRecordTypeDefinition`, `CpnControlRecordField`, `CpnControlRecord`, `CpnToken`. It selects typed
collaborators and preserves dependency direction. It does not resolve payload
bodies, invoke providers, access persistence, or grant execution authority.

## Composition strategy

Composition uses immutable values and identity-bearing operations. Child modules
own their local validation, representation, mapping, linking, or CPN semantics.
This level must not copy domain topology or merge schema admission,
authorization, firing, numerical verification, and scientific validation.

## Source

The production owner is `src/python/projectkoios/workflow/petrinet/colored/values.py`. The companion implementation and
schematics documents record dependency rules and composition flow.
