# `WorkflowCpnExecutionProfileResolutionIssue` schematics

## Local contract flow

```mermaid
flowchart LR
    typed["Declared typed constructor or operation input"] --> contract["WorkflowCpnExecutionProfileResolutionIssue"]
    contract --> retained["Explicit identity, immutable value, finding, or result"]
```

The arrows show typed data composition, not runtime scheduling.

## Coordination and authority boundary

```mermaid
flowchart TB
    collaborators["Declared typed collaborators"] --> contract["WorkflowCpnExecutionProfileResolutionIssue"]
    canonical["Bounded canonical data"] --> contract
    callbacks["Callbacks and dynamic imports"] -. "excluded" .-> contract
    effects["Providers, stores, filesystems, and networks"] -. "excluded" .-> contract
    science["Scientific acceptance or execution authorization"] -. "not granted" .-> contract
```

## Ownership

`WorkflowCpnExecutionProfileResolutionIssue` owns only its source-declared behavior. Coordinators may correlate
it with other contracts but cannot copy its semantics, recursively inline child
topology, or infer authorization from successful construction.
