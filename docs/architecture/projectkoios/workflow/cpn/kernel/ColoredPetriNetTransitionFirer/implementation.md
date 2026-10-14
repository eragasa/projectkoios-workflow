# `ColoredPetriNetTransitionFirer` implementation

## Responsibility

Implement as a pure action with closed success/failure records. Revalidate the selected binding against the exact predecessor, including read and inhibitor conditions, before producing outputs. Reject stale, substituted, missing, extra, or mistyped external variables.

The runtime commits the firing evidence and successor marking through one CAS transaction. The firer itself performs no persistence or retry.
