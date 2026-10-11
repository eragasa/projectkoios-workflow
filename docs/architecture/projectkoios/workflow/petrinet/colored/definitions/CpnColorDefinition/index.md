# `CpnColorDefinition`

## Purpose

One generic token color and its admitted tagged value kinds. Parameters ---------- identity Nominal color identity. allowed_value_kinds Nonempty unique admitted generic kinds, stored in canonical enum-value order. Workflow payload-type identities do not belong to this record. Raises ------ TypeError A field has the wrong nominal type or the kind collection is mutable. ValueError The admitted kind set is empty or contains duplicates. Notes ----- A legacy no-payload color is represented explicitly by the singleton ``NONE`` kind rather than an empty admitted set.

## Contract role

`CpnColorDefinition` is an immutable typed contract value declared by
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
