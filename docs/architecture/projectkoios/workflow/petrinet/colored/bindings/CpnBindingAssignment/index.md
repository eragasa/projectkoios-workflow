# `CpnBindingAssignment`

## Purpose

Association of one definition-owned variable with one generic value. Parameters ---------- variable_identity Nominal identity of the bound variable. value Exact immutable generic value assigned to the variable. Raises ------ TypeError A field does not have its exact owner-local nominal type.

## Contract role

`CpnBindingAssignment` is an immutable typed contract value declared by
`projectkoios.workflow.petrinet.colored.bindings`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
