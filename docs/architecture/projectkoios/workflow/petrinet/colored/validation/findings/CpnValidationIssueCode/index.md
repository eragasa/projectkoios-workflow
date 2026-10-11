# `CpnValidationIssueCode`

## Purpose

Stable semantic codes for v2 structural findings. Attributes ---------- UNKNOWN_COLOR A referenced color is absent from the definition. UNKNOWN_PLACE An arc references a place absent from the definition. UNKNOWN_TRANSITION An arc references a transition absent from the definition. COLOR_NOT_ALLOWED A pattern, template, or token color is not admitted by its place. VALUE_KIND_NOT_ALLOWED A token value kind is not admitted by its color definition. UNDECLARED_BINDING_VARIABLE A pattern or expression references a variable outside its permitted role. UNBOUND_BINDING_VARIABLE A declared input variable has no valid consume/read binder. DUPLICATE_BINDING_VARIABLE A declared input variable has multiple valid consume/read binders. EXTERNAL_OUTPUT_VARIABLE_IN_GUARD A guard references a variable reserved for external output. DEFINITION_IDENTITY_MISMATCH A marking identifies a different definition from the supplied definition. PLACE_SET_MISMATCH A marking does not contain exactly the definition's place set.

## Contract role

`CpnValidationIssueCode` is a closed enumeration declared by
`projectkoios.workflow.petrinet.colored.validation.findings`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
