# `WorkflowPluginManifestProvider` implementation

## Responsibility

Define a minimal ABC and canonical validating base. Manifest construction must be deterministic, bounded, side-effect-free, and independent of current service state. Entry-point loading occurs only in an isolated exporter or worker.

Tests cover changed wheel/environment digests, duplicate action URIs, incompatible protocol ranges, overstated lifecycle guarantees, noncanonical ordering, and attempts to embed live objects or private credentials.
