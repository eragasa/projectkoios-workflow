# `ColoredPetriNetComposer` schematic

## Responsibility

```text
fragments + connections
          │ canonicalize by identities
          │ validate ports and inheritance
          │ namespace internals
          │ resolve priorities
          │ flatten arcs/guards/inscriptions
          ▼
ColoredPetriNetComposition
  ├── definition
  ├── fragment map
  └── composition evidence
```

The produced definition is subsequently validated by the independent kernel validator.
