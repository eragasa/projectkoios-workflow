# `projectkoios.workflow.sdk` schematic

## Responsibility

```text
projectkoios-workflow-sdk (`projectkoios.workflow_sdk`)
├── source       immutable external definition inputs
├── cpn          fragment-template authoring contracts
├── actions      Workflow Firer ABC and explicit transition bindings
├── runtime      bounded occurrence/request/result correlation
├── registry     immutable integration manifests
└── worker       nominal worker-loaded integration boundary

consumer package ──encapsulates──▶ consumer-owned integration ABC
                                         │ extends
                                         ▼
                                Workflow Firer ABC
                                         │ loaded only by
                                         ▼
                                  isolated worker
                                         │ emits
                                         ▼
                               typed result and evidence
                                         │ validated by
                                         ▼
                                  Workflow service
                                         │ admitted to
                                         ▼
                         ColoredPetriNetTransitionFirer
```

The `0.1.0a1` alpha omits the effectful lifecycle module. The SDK points outward
only through immutable records and nominal ABCs. It does not import service
internals, owner packages, or the CPN kernel implementation.
