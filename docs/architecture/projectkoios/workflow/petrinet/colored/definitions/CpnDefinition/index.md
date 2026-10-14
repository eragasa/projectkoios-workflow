# `CpnDefinition`

## Purpose

One immutable identified generic colored-Petri-net definition. Parameters ---------- identity Nominal identity of this exact definition. colors, places, transitions, arcs Unique definition components stored in canonical nominal-identity order. transition_priority Exact permutation of every transition identity from highest to lowest definition-owned selection priority. Raises ------ TypeError A field has the wrong nominal type or a collection is mutable. ValueError Component identities are duplicated or priority is not an exact transition identity permutation. Notes ----- The definition contains no schema version, initial marking, descriptions, Workflow payload identifiers, or external behavior. Cross-reference integrity and semantic compatibility belong to ``CpnDefinitionValidator``.

## Contract role

`CpnDefinition` is an immutable typed contract value declared by
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
