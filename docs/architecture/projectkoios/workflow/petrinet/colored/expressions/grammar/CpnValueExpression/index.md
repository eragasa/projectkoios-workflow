# `CpnValueExpression`

## Purpose

One closed declarative generic value expression. Parameters ---------- kind Exact expression discriminant. literal Tagged literal required only for ``LITERAL``. variable_identity Nominal binding variable required only for ``VARIABLE``. Raises ------ TypeError A field has the wrong semantic or nominal type. ValueError Fields do not match exactly one expression variant.

## Contract role

`CpnValueExpression` is an immutable typed contract value declared by
`projectkoios.workflow.petrinet.colored.expressions.grammar`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
