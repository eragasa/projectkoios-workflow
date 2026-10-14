# `ColoredPetriNetMarking` implementation

## Responsibility

Use immutable place-marking tuples with canonical token ordering while preserving anonymous multiplicity. Validate every color and place against the exact definition. Identified token identities must not collide across places or generations.

Persistence stores complete predecessor/successor marking identity and firing evidence. Derived database projections may optimize queries but never replace the marking as semantic state.
