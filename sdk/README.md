# projectkoios-workflow-sdk

Pure-firing consumer integration SDK for the Project Koios CPN workflow
platform.

This `0.1.0a1` package is an unreleased alpha. It contains only immutable
standard-library records, nominal runtime-enforced abstract base classes, and
strict canonical JSON codecs. It provides no effect lifecycle, scheduler,
worker daemon, registry database, persistence, authority issuance, artifact
resolution, or production compatibility promise.

## Alpha compatibility and use

Every public surface may change or be removed before a stable release. Consumers
must pin the exact alpha version; compatibility with any other SDK version is
not promised. This package is for integration development and conformance
fixtures only. It must not be used for production execution, external effects,
credential or authority transfer, private or large payload transfer, or as a
substitute for authoritative CPN marking and occurrence history.

The authoritative architecture is maintained in
`docs/architecture/projectkoios/workflow/sdk/` in the parent repository.
