# `AbstractWorkflow`

> **Status: iteration-2 target; exact public name unaccepted.**

## Responsibility

`AbstractWorkflow` is the nominal composite specialization of `AbstractTask`.
It declares a stable identity, immutable ordered Task-instance composition, and
explicit input/export contracts.

A parent invokes a Workflow through one Task position. Runtime then creates a
distinct child Workflow run with its own plan, marking, occurrences, attempts,
history, replay, and terminal delivery. The parent never embeds or directly
advances the child's CPN.

The source class performs no discovery, persistence, scheduling, enablement,
firing, provider execution, or child-run creation. Its final definition property
constructs one generic immutable `WorkflowDefinition`.
