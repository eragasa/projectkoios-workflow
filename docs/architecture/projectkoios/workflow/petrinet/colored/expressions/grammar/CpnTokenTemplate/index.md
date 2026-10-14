# `CpnTokenTemplate`

## Purpose

Declarative template for one produced generic token. Parameters ---------- color_identity Nominal color of the produced token. value_expression Expression producing its tagged value. token_identity_expression Optional expression that must evaluate to a string when firing requires an individually correlated output token. Validation occurs during firing. Raises ------ TypeError A field has the wrong nominal expression or identity type.

## Contract role

`CpnTokenTemplate` is an immutable typed contract value declared by
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
