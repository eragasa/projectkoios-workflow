# `ColoredPetriNetComposer` implementation

## Responsibility

Expose composition as a pure typed action. Sort semantically unordered inputs by identity while preserving definition-owned ordered fields. Recompute fragment identities rather than trusting callers.

Tests compose equal fragments in different caller orders, compare the output to independently stated flat reference nets, and cover cyclic patterns, shared result tokens, fan-out, joins, retries, approval, timer, and external-effect fragments.
