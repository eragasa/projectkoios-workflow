# `ColoredPetriNetView` implementation

## Responsibility

Construct through a pure projector from bounded immutable inputs. Do not embed live objects, callbacks, mutable layout state, or unescaped markup. Layout is a renderer concern and cannot alter the view identity.

Golden fixtures cover concurrency, conflict, cycles, read and inhibitor arcs, repeated anonymous tokens, identified tokens, composition groups, and external-effect occurrence evidence.
