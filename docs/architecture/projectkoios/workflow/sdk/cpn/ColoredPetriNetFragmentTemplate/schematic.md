# `ColoredPetriNetFragmentTemplate` schematic

## Responsibility

```text
ColoredPetriNetFragmentTemplate
   ├── template identity
   ├── inheritance chain
   ├── declared extension points
   ├── public port contracts
   └── instantiate(namespace, parameters)
                         │
                         ▼
              ColoredPetriNetFragment
```

The resulting fragment is immutable and fully namespaced. Equal inputs must produce equal semantic content and identity regardless of caller order.
