# `ExternalLifecycleProvider`

> **Status: provisional architecture candidate.**

## Responsibility

`ExternalLifecycleProvider` groups the exact typed actionizers that control one registered class of external effect. It exposes an immutable provider descriptor and no generic shell command interface.

The provider owns staging, native invocation, native observation, and evidence collection. Workflow owns occurrence state, authority-token admission, dispatch intent, retry policy, reconciliation requirement, and firing admission. A grant is an exact occurrence/attempt/provider/request/resource-bound color or referenced token, never a boolean or reusable historical evidence. Cancellation authority may be separately scoped.
