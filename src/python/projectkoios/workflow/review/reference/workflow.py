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
    WorkflowDecisionReference,
    WorkflowDefinitionReference,
    WorkflowExternalReferenceIdentity,
    WorkflowIdempotencyIdentity,
    WorkflowOperationIdentity,
    WorkflowRun,
    WorkflowRunStarter,
    WorkflowRunStartResult,
    WorkflowRunStatus,
    WorkflowStateSnapshot,
    WorkflowSubjectIdentity,
    WorkflowTransitionInput,
    WorkflowTransitionRequest,
    WorkflowTypedReference,
)

from .models import (
    IngestionClaimCandidateReference,
    IngestionReferenceEvidenceReference,
    ReferenceReviewStage,
)

REFERENCE_REVIEW_CONTRACT_ID = "projectkoios.reference-review"
REFERENCE_REVIEW_CONTRACT_VERSION = "0.2.0"
EXCLUDE_REVIEWED_CLAIM_OPERATION = WorkflowOperationIdentity(
    "exclude-reviewed-claim"
)
REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION = WorkflowOperationIdentity(
    "require-manual-claim-review"
)
RETAIN_REVIEWED_CLAIM_OPERATION = WorkflowOperationIdentity(
    "retain-reviewed-claim"
)
_OPERATIONS = (
    EXCLUDE_REVIEWED_CLAIM_OPERATION,
    REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION,
    RETAIN_REVIEWED_CLAIM_OPERATION,
)
_DECISION_KIND = "manual-reference-claim-review"
_DECISION_VERSION = "1"
_DEFINITION_DIGEST = hashlib.sha256(
    json.dumps(
        {
            "contract_id": REFERENCE_REVIEW_CONTRACT_ID,
            "contract_version": REFERENCE_REVIEW_CONTRACT_VERSION,
            "stages": [stage.value for stage in ReferenceReviewStage],
            "operations": [operation.value for operation in _OPERATIONS],
            "decision_kind": _DECISION_KIND,
            "decision_version": _DECISION_VERSION,
            "claim_support_operation": None,
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


def _candidate_reference(
    candidate: IngestionClaimCandidateReference,
) -> WorkflowTypedReference:
    return WorkflowTypedReference(
        "ingestion-reference-claim-candidate",
        WorkflowExternalReferenceIdentity(candidate.identity.value),
    )


def _validate_boundary_types(
    *,
    actor_identity: object,
    authority_reference: object,
    idempotency_identity: object,
) -> None:
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


def _subject(
    evidence: IngestionReferenceEvidenceReference,
) -> WorkflowSubjectIdentity:
    return WorkflowSubjectIdentity(f"research-source:{evidence.source_sha256}")


def _validate_candidate_lineage(
    evidence: IngestionReferenceEvidenceReference,
    candidate: IngestionClaimCandidateReference,
) -> None:
    if type(evidence) is not IngestionReferenceEvidenceReference:
        raise TypeError("evidence must be IngestionReferenceEvidenceReference")
    if type(candidate) is not IngestionClaimCandidateReference:
        raise TypeError("candidate must be IngestionClaimCandidateReference")
    if (
        candidate.reference_evidence_record_identity != evidence.record_identity
        or candidate.source_blob_identity != evidence.source_blob_identity
        or candidate.source_sha256 != evidence.source_sha256
    ):
        raise ValueError("claim candidate does not match ingestion evidence")


def _manual_state_references(
    evidence: IngestionReferenceEvidenceReference,
    candidate: IngestionClaimCandidateReference,
) -> tuple[WorkflowTypedReference, ...]:
    return (
        _candidate_reference(candidate),
        _evidence_reference(evidence),
        _stage_reference(ReferenceReviewStage.MANUAL_CLAIM_REVIEW_REQUIRED),
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
            subject_identity=_subject(evidence),
            run_key=f"reference-review:{evidence.record_identity}",
            initial_state_references=(
                _evidence_reference(evidence),
                _stage_reference(
                    ReferenceReviewStage.REFERENCE_EVIDENCE_OBSERVED
                ),
            ),
        )


class IngestionEvidenceReviewAdapter:
    """Map ingestion evidence to review transitions without deciding."""

    def transition_input(
        self,
        *,
        started: WorkflowRunStartResult,
        evidence: IngestionReferenceEvidenceReference,
        candidate: IngestionClaimCandidateReference,
        actor_identity: WorkflowActorIdentity,
        authority_reference: WorkflowAuthorityReference,
        idempotency_identity: WorkflowIdempotencyIdentity,
    ) -> WorkflowTransitionInput:
        """Require manual review for one positive claim candidate."""
        if type(started) is not WorkflowRunStartResult:
            raise TypeError("started must be WorkflowRunStartResult")
        _validate_candidate_lineage(evidence, candidate)
        _validate_boundary_types(
            actor_identity=actor_identity,
            authority_reference=authority_reference,
            idempotency_identity=idempotency_identity,
        )
        definition = _definition()
        if started.run.definition_identity != definition.identity:
            raise ValueError("run belongs to another workflow definition")
        subject = _subject(evidence)
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
                _candidate_reference(candidate),
                _evidence_reference(evidence),
                WorkflowTypedReference(
                    "ingestion-extraction-artifact",
                    WorkflowExternalReferenceIdentity(
                        evidence.extraction_artifact_sha256
                    ),
                    evidence.extraction_artifact_sha256,
                ),
                WorkflowTypedReference(
                    "ingestion-reference-claim",
                    WorkflowExternalReferenceIdentity(candidate.claim_identity),
                ),
                WorkflowTypedReference(
                    "ingestion-reference-evidence-record",
                    WorkflowExternalReferenceIdentity(evidence.record_identity),
                ),
                WorkflowTypedReference(
                    "ingestion-reference-page-locator-result",
                    WorkflowExternalReferenceIdentity(
                        candidate.locator_result_identity
                    ),
                ),
                WorkflowTypedReference(
                    "ingestion-reference-page",
                    WorkflowExternalReferenceIdentity(candidate.page_identity),
                    candidate.page_text_sha256,
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
                "ingestion-evidence-review:0.2.0"
            ),
            definition_identity=definition.identity,
            request_identity=request.identity,
            prior_state_identity=started.state.identity,
            disposition=WorkflowAdapterDisposition.ENABLED,
            successor_state_references=_manual_state_references(
                evidence, candidate
            ),
            successor_run_status=started.run.status,
            reasons=(
                "automated ingestion candidate requires manual claim review",
            ),
        )
        return WorkflowTransitionInput(
            definition,
            started.run,
            started.state,
            request,
            adapter_evidence,
        )

    def decision_transition_input(
        self,
        *,
        run: WorkflowRun,
        state: WorkflowStateSnapshot,
        evidence: IngestionReferenceEvidenceReference,
        candidate: IngestionClaimCandidateReference,
        decision: WorkflowDecisionReference,
        actor_identity: WorkflowActorIdentity,
        authority_reference: WorkflowAuthorityReference,
        idempotency_identity: WorkflowIdempotencyIdentity,
    ) -> WorkflowTransitionInput:
        """Apply an exact retained/excluded human review decision."""
        if type(run) is not WorkflowRun:
            raise TypeError("run must be WorkflowRun")
        if type(state) is not WorkflowStateSnapshot:
            raise TypeError("state must be WorkflowStateSnapshot")
        if type(decision) is not WorkflowDecisionReference:
            raise TypeError("decision must be WorkflowDecisionReference")
        _validate_candidate_lineage(evidence, candidate)
        _validate_boundary_types(
            actor_identity=actor_identity,
            authority_reference=authority_reference,
            idempotency_identity=idempotency_identity,
        )
        definition = _definition()
        subject = _subject(evidence)
        if (
            run.definition_identity != definition.identity
            or state.definition_identity != definition.identity
        ):
            raise ValueError("run belongs to another workflow definition")
        if (
            run.subject_identity != subject
            or decision.subject_identity != subject
        ):
            raise ValueError("decision does not match the run subject")
        if (
            run.current_state_identity != state.identity
            or run.revision != state.revision
            or run.status != state.run_status
        ):
            raise ValueError("run and state do not identify one revision")
        if state.state_references != _manual_state_references(
            evidence, candidate
        ):
            raise ValueError("run is not at the exact manual-review state")
        if (
            decision.decision_kind != _DECISION_KIND
            or decision.scope != candidate.candidate_identity
            or decision.decision_version != _DECISION_VERSION
        ):
            raise ValueError("decision does not satisfy the review contract")
        outcomes = {
            ReferenceReviewStage.REVIEWED_EXCLUDED.value: (
                EXCLUDE_REVIEWED_CLAIM_OPERATION,
                ReferenceReviewStage.REVIEWED_EXCLUDED,
            ),
            ReferenceReviewStage.REVIEWED_RETAINED.value: (
                RETAIN_REVIEWED_CLAIM_OPERATION,
                ReferenceReviewStage.REVIEWED_RETAINED,
            ),
        }
        selected = outcomes.get(decision.outcome)
        if selected is None:
            raise ValueError("decision outcome is not retained or excluded")
        operation, successor_stage = selected
        request = WorkflowTransitionRequest.create(
            run_identity=run.identity,
            expected_prior_state_identity=state.identity,
            expected_revision=run.revision,
            operation_identity=operation,
            input_references=(
                _candidate_reference(candidate),
                _evidence_reference(evidence),
            ),
            artifact_references=(),
            decision_references=(decision,),
            actor_identity=actor_identity,
            authority_reference=authority_reference,
            idempotency_identity=idempotency_identity,
        )
        adapter_evidence = WorkflowAdapterEvidence.create(
            adapter_identity=WorkflowAdapterIdentity(
                "ingestion-evidence-review:0.2.0"
            ),
            definition_identity=definition.identity,
            request_identity=request.identity,
            prior_state_identity=state.identity,
            disposition=WorkflowAdapterDisposition.ENABLED,
            successor_state_references=(
                _candidate_reference(candidate),
                _evidence_reference(evidence),
                _stage_reference(successor_stage),
            ),
            successor_run_status=WorkflowRunStatus.COMPLETED,
            reasons=(f"human claim review recorded {decision.outcome}",),
        )
        return WorkflowTransitionInput(
            definition,
            run,
            state,
            request,
            adapter_evidence,
        )
