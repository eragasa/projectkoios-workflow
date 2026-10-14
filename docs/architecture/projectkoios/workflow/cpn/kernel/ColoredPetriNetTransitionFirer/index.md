# `ColoredPetriNetTransitionFirer`

## Responsibility

`ColoredPetriNetTransitionFirer` performs one pure, identity-closed CPN firing from an exact predecessor marking and selected binding. For an effect-bound transition it also validates an explicit identified external-output binding.

It consumes exact `CONSUME` occurrences, preserves `READ` occurrences, confirms inhibitors, evaluates output inscriptions, enforces capacity, and produces successor marking plus audit evidence. In the lifecycle-subnet candidate, `begin_occurrence` and `commit_occurrence` are separate pure CPN firings; only the success commit emits the reserved logical/domain outputs.
