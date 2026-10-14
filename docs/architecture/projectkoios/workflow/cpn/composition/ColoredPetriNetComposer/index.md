# `ColoredPetriNetComposer`

## Responsibility

`ColoredPetriNetComposer` deterministically lowers a complete fragment and connection set into one ordinary CPN definition plus composition evidence. It is the only component authorized to join fragment namespaces and resolve their declared global priority policy.

It does not load templates, discover packages, construct runtime markings, or retain live source owners.
