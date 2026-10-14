# `projectkoios.workflow.compilation.definitions` architecture

## Responsibility

The definitions module owns frozen generic snapshots produced from external source owners. It erases live Python ownership while retaining exact workflow identity, task/action identity, route kind, fragment declarations, and contract references required for compilation.

Definitions are compiler inputs, not executable markings and not deployment bindings. They contain no provider object, authority, repository, run, result, or callable.
