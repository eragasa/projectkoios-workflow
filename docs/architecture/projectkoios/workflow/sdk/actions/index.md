# `projectkoios.workflow.sdk.actions` architecture

> **Status:** the implemented SDK exposes pure firing records and `Firer`; the
> broader iteration-2 Task source model remains proposed.

## Responsibility

The actions module defines the adapter boundary between one reserved selected
CPN binding and an external owner's pure atomic Task implementation. It maps
admitted owner inputs to a firing request and maps a successful correlated owner
result to identified external variables plus separately retained evidence.

An action is execution behavior or a typed command; it is not the durable Task
definition. The future Task definition names the exact action/firer descriptor,
while the run-scoped Task invocation, occurrence, and attempt retain execution
identity.

Explicit descriptors are compiler inputs. Request/result contracts declare
bounded typed ports; stable firer identity binds behavior; pure classification
selects the pure route. Effect lifecycle and workflow-backed Task execution use
separate contracts and must not be hidden behind `Firer`.

Adapters cannot inspect or mutate authoritative markings. The engine alone
validates output colors and commits firing. The compiler never infers topology,
retry, concurrency, acceptance, or child behavior from Python signatures.
