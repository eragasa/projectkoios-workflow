# `CpnGuardExpression`

## Purpose

One pure Boolean expression with operator-specific arity. Parameters ---------- operator Closed Boolean or comparison operator. operands Ordered nested guards for ``ALL``, ``ANY``, or ``NOT``. left, right Value expressions required by comparison operators. Raises ------ TypeError A field has the wrong semantic type. ValueError Fields violate the selected operator's exact arity.

## Contract role

`CpnGuardExpression` is an immutable typed contract value declared by
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
