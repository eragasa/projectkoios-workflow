# `ColoredPetriNetMarking` schematic

## Responsibility

```text
place A → [anonymous token × 3, identified token X]
place B → []
place C → [identified evidence token Y]

marking identity = canonical definition-bound multiset content
```

Reservations refer to exact token occurrences. `READ` retains them, `CONSUME` removes them on firing, and `INHIBIT` requires their absence.
