# `projectkoios.workflow.sdk.source` implementation

## Responsibility

Provide nominal runtime-enforced source ABCs, not structural protocols. The
candidate relationship is `AbstractWorkflow(AbstractTask)`: every Workflow can
occupy one Task position in a parent composition, while an atomic Task cannot
claim Workflow composition behavior.

A final definition constructor validates exact built-in fields, immutable Task
instance order, unique identities, route closure, and child definition
references. It returns frozen generic definitions and retains no owner object,
callable, handler, firer, repository, provider, path, or payload body.

Atomic Task declarations distinguish pure `Firer` execution from effectful
lifecycle execution. Workflow declarations instead provide composition and
child export contracts. They do not pretend that a complete child Workflow is
an atomic provider call. Direct and indirect self-nesting are rejected.

Historical `ksdft2effmass` Task/Workflow source patterns are migration evidence,
not a class layout to copy. Simulations' nominal QE/VASP Task records and
handlers are provider-specialization evidence. Exact APIs are accepted only
after both owner shapes pass adapters and dependency checks.
