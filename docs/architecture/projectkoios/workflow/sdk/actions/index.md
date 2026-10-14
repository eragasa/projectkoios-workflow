# `projectkoios.workflow.sdk.actions` architecture

> **Status: provisional architecture candidate.** This boundary expresses an
> authoring principle, not authorization to refactor owner packages.

## Responsibility

The actions module defines the adapter boundary between a reserved selected CPN binding and an external owner's typed action. It maps tokens to a `DataObjectActionRequest` and a successful typed result to an identified `ExternalOutputBinding`.

Explicit action descriptors are compiler inputs. Request and result contracts declare candidate typed ports and token colors; stable action identity binds transition behavior; pure/effectful classification selects pure-transition or lifecycle-fragment lowering; authority, idempotency, and evidence contracts declare required operational tokens. An owner-owned atomic composite action remains one transition boundary.

Action adapters cannot inspect or mutate the authoritative marking. They receive immutable occurrence context and bounded typed envelopes. The engine alone validates output colors and commits a firing. The compiler never infers scientific topology, guards, concurrency, retry, or acceptance from Python signatures, and it never reflectively auto-wires actions. Workflow source definitions connect every action explicitly.
