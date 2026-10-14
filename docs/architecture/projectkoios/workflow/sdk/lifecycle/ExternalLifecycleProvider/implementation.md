# `ExternalLifecycleProvider` implementation

## Responsibility

Implementations run only in isolated workers. Launch uses an allowlisted absolute executable or scheduler adapter, exact argument vectors, `shell=False`, a dedicated process group, private attempt workspace, and bounded resources.

The start ledger binds start key, canonical request digest, authorization grant, provider/environment identity, and generation-safe job handle before acknowledgement. Tests cover crashes before and after launch, duplicate starts, PID reuse, cancellation races, provider restart, authority expiry, evidence tampering, and redaction.
