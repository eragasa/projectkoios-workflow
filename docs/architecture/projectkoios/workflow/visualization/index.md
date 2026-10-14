# `projectkoios.workflow.visualization` architecture

## Responsibility

Visualization owns a deterministic, read-only projection of exact CPN and composition evidence. It presents topology, markings, token colors and multiplicities, enabled bindings, selected behavior, firing differences, fragment groupings, and privacy-reduced provenance.

It never independently computes enabledness, selects a binding, fires a transition, dispatches an effect, changes a marking, or grants authority.
