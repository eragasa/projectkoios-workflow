"""Verification for ingestion-evidence manual-review workflow."""

from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path

import pytest
from projectkoios.workflow.core import (
    WorkflowActorIdentity,
    WorkflowAuthorityReference,
    WorkflowExternalReferenceIdentity,
    WorkflowIdempotencyIdentity,
    WorkflowTransitionOutcomeKind,
    WorkflowTransitionPreflightInput,
)
from projectkoios.workflow.persistence import SQLiteAtomicRevisionStore
from projectkoios.workflow.reference_review import (
    REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION,
    IngestionEvidenceReviewAdapter,
    IngestionReferenceEvidenceReference,
    ReferenceReviewStage,
    ReferenceReviewWorkflow,
)
from projectkoios.workflow.runtime import (
    LocalWorkflowRuntime,
    WorkflowRuntimeActionStatus,
    WorkflowRuntimeRepository,
)


def evidence() -> IngestionReferenceEvidenceReference:
    source_digest = "a" * 64
    return IngestionReferenceEvidenceReference.create(
        record_identity=f"reference-evidence-record:sha256:{'b' * 64}",
        source_blob_identity=f"blob:sha256:{source_digest}",
        source_sha256=source_digest,
        source_byte_length=12_345,
        source_media_type="application/pdf",
        extraction_artifact_sha256="c" * 64,
        transcript_artifact_sha256="d" * 64,
        audit_artifact_sha256="e" * 64,
    )


def test__reference_review__uses_ingestion_evidence_as_non_authorizing_input(
    tmp_path: Path,
) -> None:
    selected = evidence()
    workflow = ReferenceReviewWorkflow()
    started = workflow.start(selected)
    authority = WorkflowAuthorityReference.create(
        authority_kind="local-reference-review-policy",
        subject_identity=started.run.subject_identity,
        operation_identities=(REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION,),
        evidence_identity=WorkflowExternalReferenceIdentity(
            "policy:reference-review:fixture"
        ),
        authority_version="1",
    )
    transition_input = IngestionEvidenceReviewAdapter().transition_input(
        started=started,
        evidence=selected,
        actor_identity=WorkflowActorIdentity("operator:reviewer"),
        authority_reference=authority,
        idempotency_identity=WorkflowIdempotencyIdentity(
            "reference-review:fixture:1"
        ),
    )
    runtime = LocalWorkflowRuntime(
        WorkflowRuntimeRepository(
            SQLiteAtomicRevisionStore(
                tmp_path / "private" / "reference-review.sqlite3"
            )
        )
    )

    start_result = runtime.start(started)
    retained = runtime.retain_request(
        WorkflowTransitionPreflightInput(
            transition_input.definition,
            transition_input.run,
            transition_input.prior_state,
            transition_input.request,
        )
    )
    transitioned = runtime.record_transition(transition_input)

    assert start_result.status is WorkflowRuntimeActionStatus.RECORDED
    assert retained.status is WorkflowRuntimeActionStatus.RECORDED
    assert transitioned.status is WorkflowRuntimeActionStatus.RECORDED
    assert transitioned.transition is not None
    assert transitioned.transition.outcome.kind is (
        WorkflowTransitionOutcomeKind.APPLIED
    )
    assert transitioned.transition.outcome.successor_state is not None
    assert {
        reference.reference_identity.value
        for reference in (
            transitioned.transition.outcome.successor_state.state_references
        )
    } == {
        selected.identity.value,
        ReferenceReviewStage.MANUAL_CLAIM_REVIEW_REQUIRED.value,
    }
    assert transition_input.request.authority_reference == authority
    assert all(
        "authority" not in field.name
        for field in fields(IngestionReferenceEvidenceReference)
    )


def test__reference_review__admits_no_acceptance_or_publication_operation() -> (
    None
):
    definition = ReferenceReviewWorkflow().definition

    assert definition.operation_identities == (
        REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION,
    )
    assert "published" not in {stage.value for stage in ReferenceReviewStage}
    assert not any(
        word in operation.value
        for operation in definition.operation_identities
        for word in ("accept", "publish", "retain", "exclude")
    )


def test__ingestion_evidence__is_exact_and_fails_closed() -> None:
    selected = evidence()

    assert evidence() == selected
    with pytest.raises(ValueError, match="source blob identity"):
        IngestionReferenceEvidenceReference.create(
            record_identity=selected.record_identity,
            source_blob_identity=f"blob:sha256:{'f' * 64}",
            source_sha256=selected.source_sha256,
            source_byte_length=selected.source_byte_length,
            source_media_type=selected.source_media_type,
            extraction_artifact_sha256=selected.extraction_artifact_sha256,
            transcript_artifact_sha256=selected.transcript_artifact_sha256,
            audit_artifact_sha256=selected.audit_artifact_sha256,
        )
    with pytest.raises(ValueError, match="automated_unreviewed"):
        replace(selected, transcript_status="reviewed")
    with pytest.raises(ValueError, match="inconsistent"):
        replace(selected, audit_artifact_sha256="f" * 64)
