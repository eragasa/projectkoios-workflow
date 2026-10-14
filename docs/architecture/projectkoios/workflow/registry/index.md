# `projectkoios.workflow.registry` architecture

## Responsibility

The registry owns immutable definition snapshots, compiled plans, action descriptors, provider capability descriptors, deployment bindings, compatibility metadata, and availability projections. It distinguishes catalog identity from current availability.

Registration never imports domain packages into the service. External exporters and workers submit canonical manifests through authenticated action operations. Existing versions are never overwritten.
