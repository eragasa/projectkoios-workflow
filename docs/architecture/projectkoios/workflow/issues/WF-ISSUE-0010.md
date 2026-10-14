# WF-ISSUE-0010 — EPW real-execution conformance evidence

- **Kind:** evidence
- **Status:** BLOCKED_BY_DEPENDENCY
- **Workflow-local scope:** claims supported by the generic external lifecycle protocol
- **Authoritative owner:** `projectkoios-simulations`

## Problem or question

Can the proposed external-job lifecycle claim real EPW execution conformance when current EPW tests use local shell stubs and no retained real EPW run fixture exists?

## Current evidence

Simulations inventory at `f3e7ee568434313b0c36e7e304484a4fac6e0a63` identifies `integrations/quantumespresso/epw/execution.py` and provider-side EPW input, stream, and artifact semantics. Tests exercise bounded runner behavior through stubs; no committed real native execution package validates job identity, output completeness, or domain normalization.

## Consequence

Generic architecture and non-EPW vertical slices may proceed through review, but EPW production readiness and real-execution compatibility claims remain blocked.

## Alternatives and recommendation

Retain stub tests as software-boundary evidence without relabeling them. Obtain a separately authorized, privacy-reviewed, content-addressed retained EPW execution fixture before asserting real provider conformance.

## Resolution gate

An owner-controlled fixture binds executable/environment, inputs, job lifecycle, outputs, diagnostics, hashes, normalization, and independent verification under the accepted provider protocol.

## Affected architecture

Provider conformance matrix, external lifecycle evidence schemas, and EPW workflow migration status.
