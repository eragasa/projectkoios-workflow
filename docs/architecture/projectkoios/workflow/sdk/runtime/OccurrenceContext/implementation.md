# `OccurrenceContext` implementation

> **Status: provisional architecture candidate.**

## Responsibility

Construction would occur only after exact enablement, selection, and reservation checks. Workers receive an immutable serialized context and echo its relevant identities and canonical request digest in every observation.

Conformance must reject changed definition, marking revision, token set, binding, attempt ordinal, request digest, job-handle generation, and out-of-order observation revision. Whether token IDs are exposed individually depends on privacy and size bounds; a digest cannot replace retained exact reservation evidence inside Workflow.
