"""Pure review workflow for ingestion-owned reference evidence."""

from __future__ import annotations

import hashlib
import json

from projectkoios.workflow.core import (
    WorkflowActorIdentity,
    WorkflowAdapterDisposition,
    WorkflowAdapterEvidence,
    WorkflowAdapterIdentity,
    WorkflowAuthorityReference,
    WorkflowDefinitionReference,
    WorkflowExternalReferenceIdentity,
    WorkflowIdempotencyIdentity,
    WorkflowOperationIdentity,
    WorkflowRunStarter,
    WorkflowRunStartResult,
    WorkflowSubjectIdentity,
    WorkflowTransitionInput,
    WorkflowTransitionRequest,
    WorkflowTypedReference,
)

from .models import (
    IngestionReferenceEvidenceReference,
    ReferenceReviewStage,
)

REFERENCE_REVIEW_CONTRACT_ID = "projectkoios.reference-review"
REFERENCE_REVIEW_CONTRACT_VERSION = "0.1.0"
REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION = WorkflowOperationIdentity(
    "require-manual-claim-review"
)
_OPERATIONS = (REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION,)
_DEFINITION_DIGEST = hashlib.sha256(
    json.dumps(
        {
            "contract_id": REFERENCE_REVIEW_CONTRACT_ID,
            "contract_version": REFERENCE_REVIEW_CONTRACT_VERSION,
            "stages": [stage.value for stage in ReferenceReviewStage],
            "operations": [operation.value for operation in _OPERATIONS],
            "publication_operation": None,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
).hexdigest()


def _definition() -> WorkflowDefinitionReference:
    return WorkflowDefinitionReference.create(
        contract_id=REFERENCE_REVIEW_CONTRACT_ID,
        definition_version=REFERENCE_REVIEW_CONTRACT_VERSION,
        definition_digest_sha256=_DEFINITION_DIGEST,
        operation_identities=_OPERATIONS,
    )


def _stage_reference(stage: ReferenceReviewStage) -> WorkflowTypedReference:
    return WorkflowTypedReference(
        "reference-review-stage",
        WorkflowExternalReferenceIdentity(stage.value),
    )


def _evidence_reference(
    evidence: IngestionReferenceEvidenceReference,
) -> WorkflowTypedReference:
    return WorkflowTypedReference(
        "ingestion-reference-evidence",
        WorkflowExternalReferenceIdentity(evidence.identity.value),
    )


class ReferenceReviewWorkflow:
    """Start review runs from complete, unreviewed ingestion evidence."""

    @property
    def definition(self) -> WorkflowDefinitionReference:
        """Return the immutable reference-review definition."""
        return _definition()

    def start(
        self,
        evidence: IngestionReferenceEvidenceReference,
    ) -> WorkflowRunStartResult:
        """Create revision zero without claim or publication authority."""
        if type(evidence) is not IngestionReferenceEvidenceReference:
            raise TypeError(
                "evidence must be IngestionReferenceEvidenceReference"
            )
        return WorkflowRunStarter().execute(
            definition=self.definition,
            subject_identity=WorkflowSubjectIdentity(
                f"research-source:{evidence.source_sha256}"
            ),
            run_key=f"reference-review:{evidence.record_identity}",
            initial_state_references=(
                _evidence_reference(evidence),
                _stage_reference(
                    ReferenceReviewStage.REFERENCE_EVIDENCE_OBSERVED
                ),
            ),
        )


class IngestionEvidenceReviewAdapter:
    """Map verified ingestion metadata to a manual-review requirement."""

    def transition_input(
        self,
        *,
        started: WorkflowRunStartResult,
        evidence: IngestionReferenceEvidenceReference,
        actor_identity: WorkflowActorIdentity,
        authority_reference: WorkflowAuthorityReference,
        idempotency_identity: WorkflowIdempotencyIdentity,
    ) -> WorkflowTransitionInput:
        """Return core input without parsing, dispatch, or acceptance."""
        if type(started) is not WorkflowRunStartResult:
            raise TypeError("started must be WorkflowRunStartResult")
        if type(evidence) is not IngestionReferenceEvidenceReference:
            raise TypeError(
                "evidence must be IngestionReferenceEvidenceReference"
            )
        for value, expected, name in (
            (actor_identity, WorkflowActorIdentity, "actor_identity"),
            (
                authority_reference,
                WorkflowAuthorityReference,
                "authority_reference",
            ),
            (
                idempotency_identity,
                WorkflowIdempotencyIdentity,
                "idempotency_identity",
            ),
        ):
            if type(value) is not expected:
                raise TypeError(f"{name} has an invalid nominal type")
        definition = _definition()
        if started.run.definition_identity != definition.identity:
            raise ValueError("run belongs to another workflow definition")
        subject = WorkflowSubjectIdentity(
            f"research-source:{evidence.source_sha256}"
        )
        if started.run.subject_identity != subject:
            raise ValueError("evidence source does not match the run subject")
        expected_state = (
            _evidence_reference(evidence),
            _stage_reference(ReferenceReviewStage.REFERENCE_EVIDENCE_OBSERVED),
        )
        if started.state.state_references != expected_state:
            raise ValueError("run is not at the exact evidence-observed state")
        request = WorkflowTransitionRequest.create(
            run_identity=started.run.identity,
            expected_prior_state_identity=started.state.identity,
            expected_revision=started.run.revision,
            operation_identity=REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION,
            input_references=(
                WorkflowTypedReference(
                    "ingestion-audit-artifact",
                    WorkflowExternalReferenceIdentity(
                        evidence.audit_artifact_sha256
                    ),
                    evidence.audit_artifact_sha256,
                ),
                _evidence_reference(evidence),
                WorkflowTypedReference(
                    "ingestion-extraction-artifact",
                    WorkflowExternalReferenceIdentity(
                        evidence.extraction_artifact_sha256
                    ),
                    evidence.extraction_artifact_sha256,
                ),
                WorkflowTypedReference(
                    "ingestion-reference-evidence-record",
                    WorkflowExternalReferenceIdentity(evidence.record_identity),
                ),
                WorkflowTypedReference(
                    "ingestion-source-blob",
                    WorkflowExternalReferenceIdentity(
                        evidence.source_blob_identity
                    ),
                    evidence.source_sha256,
                ),
                WorkflowTypedReference(
                    "ingestion-transcript-artifact",
                    WorkflowExternalReferenceIdentity(
                        evidence.transcript_artifact_sha256
                    ),
                    evidence.transcript_artifact_sha256,
                ),
            ),
            artifact_references=(),
            decision_references=(),
            actor_identity=actor_identity,
            authority_reference=authority_reference,
            idempotency_identity=idempotency_identity,
        )
        adapter_evidence = WorkflowAdapterEvidence.create(
            adapter_identity=WorkflowAdapterIdentity(
                "ingestion-evidence-review:0.1.0"
            ),
            definition_identity=definition.identity,
            request_identity=request.identity,
            prior_state_identity=started.state.identity,
            disposition=WorkflowAdapterDisposition.ENABLED,
            successor_state_references=(
                _evidence_reference(evidence),
                _stage_reference(
                    ReferenceReviewStage.MANUAL_CLAIM_REVIEW_REQUIRED
                ),
            ),
            successor_run_status=started.run.status,
            reasons=(
                "automated ingestion evidence requires manual claim review",
            ),
        )
        return WorkflowTransitionInput(
            definition,
            started.run,
            started.state,
            request,
            adapter_evidence,
        )
