# `projectkoios.workflow.compilation.planning` implementation

## Responsibility

The constructor returns either one complete plan or closed findings. It never
returns a plan with unresolved Task instances, ports, routes, mappings,
priorities, child targets, or export contracts.

Plans are canonically serialized and content-addressed. Parent plans retain
exact child-plan references and route contracts, not embedded child graphs. Live
source owners, configured owner Tasks, handlers, firers, providers, repositories,
paths, and payloads are forbidden fields and must be excluded by closed record
types rather than convention.

Compilation rejects direct or indirect Workflow cycles, a Task definition used
under the wrong specialization, missing child inputs/exports, and parent mapping
that depends on unadmitted child state.
