# `projectkoios.workflow.cli` implementation

## Responsibility

Implement the CLI as a thin client package with no database or plugin imports. Commands map one-to-one to typed service operations and support machine-readable output without exposing sealed locators or secrets.

Mutating commands require explicit verbs and idempotency identities. Destructive history rewrite and arbitrary shell-command dispatch are intentionally absent.
