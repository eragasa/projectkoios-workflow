# `WorkflowExecutionBindings`

## Responsibility

`WorkflowExecutionBindings` is the immutable result of deployment linking for
one exact plan. It records the complete ordered correspondence among compiled
transition/action mappings and registered provider, worker, environment, or
nested-target handles.

For a pure external action it also identifies the exact retained result-mapping
descriptor already selected by the execution plan. Deployment linking proves
that the installed worker and provider implement that exact descriptor; it does
not select or revise semantic mapping independently of the plan. The descriptor
binds owner output and evidence roles, schemas, codecs, representations, and
bounds to declared CPN external variables without retaining owner objects or
executable callables.

The QE SCF artifact-set direction links the future `artifact_set_identity`
logical output to one declared string variable while retaining the canonical
`artifact_set` document as evidence. The binding never treats the evidence
payload digest as the owner logical identity.

This artifact is not part of the plan's semantic identity and contains no live
implementation objects. Runtime provenance records its selected identities.
Changing a provider or environment produces another deployment-binding artifact;
changing a mapping descriptor requires a new execution-plan identity and then a
new deployment binding for that plan.
