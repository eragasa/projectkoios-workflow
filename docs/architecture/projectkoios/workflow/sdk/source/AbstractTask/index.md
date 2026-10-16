# `AbstractTask`

> **Status: iteration-2 target; exact public name unaccepted.**

## Responsibility

`AbstractTask` is the nominal source-language owner for one parent-visible unit
of work. It supplies a stable identity and a final immutable-definition
boundary. Concrete specializations are either atomic Tasks or composite
Workflows.

An atomic Task declares exactly one execution route: pure owner firing or an
accepted effect lifecycle. A Workflow declares composition and is itself a Task
when used by a parent. Runtime occurrence, attempt, result, and run identities
remain separate from source Task identity.

The source Task is not a durable runtime object and executes nothing. Actions,
events, CPN transitions, handlers, firers, and provider records are related
contracts, not subclasses merely because they participate in execution.
