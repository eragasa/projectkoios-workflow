# `projectkoios.workflow.sdk.runtime` implementation

> **Status: provisional architecture candidate.**

## Responsibility

Use frozen slotted records with canonical content identities and strict serialization bounds. Separate public correlation identity from sealed operational locators. Context must contain enough evidence to reject stale worker replies without embedding the complete private marking or domain payload.

Open questions include whether bound token identities are carried directly or by a bounded digest plus retained reservation reference, and how parent net-instance correlation is represented after composition and linking.
