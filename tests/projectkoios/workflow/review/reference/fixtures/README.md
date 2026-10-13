# Reference-review conformance fixtures

`ingestion-claim-candidate.json` was produced by
`projectkoios-ingestion` contract
`projectkoios.ingestion.reference-claim-candidate@0.1.0` from its synthetic
reference-evidence and whole-token page-locator fixture. It contains no source,
page, quotation, or claim text.

The workflow test treats the JSON field inventory as an exact producer-consumer
boundary and constructs `IngestionClaimCandidateReference` without importing or
reimplementing ingestion. Changes to either contract require regenerating and
reviewing this fixture in both owning repositories; the fixture does not grant
review or publication authority.
