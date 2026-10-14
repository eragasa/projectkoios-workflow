# `AbstractTask` implementation

## Responsibility

Adapt the nominal route-root behavior of historical `AbstractTask` without restoring its earlier executable graph as the runtime truth. The base must reject ambiguous or inherited conflicting route declarations and construct a frozen generic definition.

Pure actions should still execute in isolated workers rather than the orchestrator process. External effects require lifecycle bindings. Nested targets require exact definition closure. Tests cover route inheritance, identity consistency, prohibited effect shapes, and definition stability.
