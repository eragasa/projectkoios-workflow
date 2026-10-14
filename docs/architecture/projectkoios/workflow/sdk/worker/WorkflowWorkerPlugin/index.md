# `WorkflowWorkerPlugin`

## Responsibility

`WorkflowWorkerPlugin` is the nominal composition root for provider code loaded in one isolated worker environment. It supplies the canonical manifest source and the exact action/lifecycle implementations named by that manifest.

It cannot register arbitrary commands, discover other plugins, mutate a plan, or select work outside its advertised capability scope.
