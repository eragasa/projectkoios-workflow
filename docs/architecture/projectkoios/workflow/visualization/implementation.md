# `projectkoios.workflow.visualization` implementation

## Responsibility

Implement the read-only view contract from Frankenstein visualization design evidence. Projection output should be deterministic for identical inputs, escape all values and annotations, expose non-color labels, and support accessible inspection.

The generic Web component consumes this projection or its stable wire schema. Any mutation controls belong to separately authenticated application/control APIs, not to the visualizer.
