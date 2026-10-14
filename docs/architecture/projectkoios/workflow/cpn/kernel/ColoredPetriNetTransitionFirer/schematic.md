# `ColoredPetriNetTransitionFirer` schematic

## Responsibility

```text
predecessor marking
+ exact selected binding
+ optional external-output binding
                 │ validate closure
                 ▼
 consume / retain / confirm absence / produce
                 │
                 ▼
successor marking + firing audit
```

Provider failure or ambiguity never reaches this operation as a successful external-output binding.
