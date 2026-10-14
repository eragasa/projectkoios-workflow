# `projectkoios.workflow.sdk.worker` implementation

## Responsibility

Define immutable plugin identity and tuple-returning accessors for registered components. A validating base checks that every exposed implementation agrees with the package manifest and that no unadvertised action can be invoked.

Loading, authentication, leases, heartbeat, drain, and process supervision remain responsibilities of the generic worker host.
