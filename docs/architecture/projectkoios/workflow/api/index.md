# `projectkoios.workflow.api` architecture

## Responsibility

The API package adapts authenticated local transport to control-plane action requests and results. It owns serialization, transport authentication, request bounds, error mapping, and event/status subscription delivery.

It does not contain workflow semantics, provider code, credentials for protected effects, or application-specific orchestration. Applications may wrap the stable client/API in higher-level use-case surfaces.
