# `projectkoios.workflow.cpn.composition` schematic

## Responsibility

```text
fragment A ports ─┐
fragment B ports ─┼─ typed connections ─▶ composer ─▶ flat CPN
fragment C ports ─┘                         │
                                           └─ composition evidence
```

Internal identities are deterministically namespaced. Fragment input order cannot alter the resulting semantic definition identity.
