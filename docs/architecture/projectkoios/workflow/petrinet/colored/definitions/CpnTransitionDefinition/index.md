# `CpnTransitionDefinition`

## Purpose

One generic transition with declared variable order and a pure guard. Parameters ---------- identity Nominal transition identity. input_variable_identities Unique variables in exact definition-declared input-binding order. external_output_variable_identities Unique variables supplied only through the future explicit external-output binding. The two collections are disjoint. guard Closed pure guard; use ``TRUE`` for an unconditional transition. Raises ------ TypeError A field has the wrong nominal type or variable collection is mutable. ValueError A binding variable identity occurs more than once.

## Contract role

`CpnTransitionDefinition` is an immutable typed contract value declared by
`projectkoios.workflow.petrinet.colored.definitions`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
