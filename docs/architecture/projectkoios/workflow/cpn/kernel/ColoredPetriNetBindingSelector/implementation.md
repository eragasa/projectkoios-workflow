# `ColoredPetriNetBindingSelector` implementation

## Responsibility

Reject directives naming a stale definition, marking, enablement result, transition, or binding. Default selection uses declared priority and canonical binding order; import order and tuple accident must not influence it.

Replay retains the original selection evidence and does not select again against a later environment.
