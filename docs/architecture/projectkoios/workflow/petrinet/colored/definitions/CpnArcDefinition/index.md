# `CpnArcDefinition`

## Purpose

One identified directed arc with exactly one inscription variant. Parameters ---------- identity Nominal arc identity. place_identity Referenced nominal place identity. transition_identity Referenced nominal transition identity. input_inscription Input demand for a place-to-transition arc, mutually exclusive with output. output_inscription Output templates for a transition-to-place arc, mutually exclusive with input. Raises ------ TypeError A field has the wrong nominal type. ValueError Both inscription variants are present or both are absent. Notes ----- Direction is derived from the closed inscription variant and is not duplicated as independent state.

## Contract role

`CpnArcDefinition` is an immutable typed contract value declared by
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
