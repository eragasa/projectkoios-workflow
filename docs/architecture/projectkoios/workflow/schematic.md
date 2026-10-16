# `projectkoios.workflow` schematic

> **Status: provisional architecture iteration 2.** The composition model is a
> target informed by owner evidence; implemented SDK alpha types remain narrower.

## Responsibility

This schematic separates owner Task definitions, Workflow composition,
compilation, deployment linking, and the three execution routes.

```mermaid
flowchart TD
    OT[Owner Task definitions]
    OW[Owner Workflow definition<br/>composite Task]
    TI[Ordered Task instances]
    SD[Immutable source definitions]
    CP[Compiler and fragment composer]
    PP[Parent WorkflowExecutionPlan<br/>flat canonical CPN]
    LK[Deployment binding linker]
    DB[Exact execution bindings]
    RT[Workflow runtime]
    PA[Pure atomic Task<br/>SDK Firer]
    EF[Effectful atomic Task<br/>lifecycle handler]
    CW[Workflow-backed Task<br/>child-run service]
    CR[Distinct child Workflow run]
    CC[Separately compiled child plan<br/>flat canonical CPN]
    CM[Atomic parent firing after<br/>admitted terminal delivery]

    OT --> TI
    OW --> TI
    TI --> SD
    SD --> CP
    CP --> PP
    PP --> LK
    LK --> DB
    DB --> RT
    RT --> PA
    RT --> EF
    RT --> CW
    CW --> CR
    CC --> CR
    PA --> CM
    EF --> CM
    CR --> CM
```

A parent composition sees every member as a Task. The workflow-backed route does
not merge child topology or history into the parent. It retains a distinct child
run and admits only an explicitly correlated terminal delivery before the
parent's pure CPN firing.

Owner-specific implementations remain outside retained generic state. For
example, QE and VASP may specialize one Simulations Task role with different
resources and handlers while the parent SCF Workflow remains calculator-neutral.
Registry discovery precedes compilation and linking; runtime receives exact
artifacts and performs no provider discovery.
