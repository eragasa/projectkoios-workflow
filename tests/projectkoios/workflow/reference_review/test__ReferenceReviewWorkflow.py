"""Verification for ingestion-evidence manual-review workflow."""

from __future__ import annotations

import json
from dataclasses import fields, replace
from pathlib import Path

import pytest
from projectkoios.workflow.core import (
    WorkflowActorIdentity,
    WorkflowAuthorityReference,
    WorkflowDecisionReference,
    WorkflowExternalReferenceIdentity,
    WorkflowIdempotencyIdentity,
    WorkflowRunStatus,
    WorkflowTransitionOutcomeKind,
    WorkflowTransitionPreflightInput,
)
from projectkoios.workflow.persistence import SQLiteAtomicRevisionStore
from projectkoios.workflow.reference_review import (
    EXCLUDE_REVIEWED_CLAIM_OPERATION,
    REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION,
    RETAIN_REVIEWED_CLAIM_OPERATION,
    IngestionClaimCandidateReference,
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


def candidate() -> IngestionClaimCandidateReference:
    source_digest = "a" * 64
    return IngestionClaimCandidateReference.create(
        candidate_identity=f"reference-claim-candidate:sha256:{'1' * 64}",
        claim_identity=f"research-claim:sha256:{'2' * 64}",
        reference_evidence_record_identity=(
            f"reference-evidence-record:sha256:{'b' * 64}"
        ),
        locator_result_identity=(
            f"reference-page-locator-result:sha256:{'3' * 64}"
        ),
        source_blob_identity=f"blob:sha256:{source_digest}",
        source_sha256=source_digest,
        transcript_identity=(f"clean-transcript-artifact:sha256:{'4' * 64}"),
        page_identity=f"clean-transcript-page:sha256:{'5' * 64}",
        page_index=7,
        page_text_sha256="6" * 64,
        page_text_utf8_byte_length=321,
        matched_topic_anchor_identities=(
            f"reference-topic-anchor:sha256:{'7' * 64}",
        ),
    )


def authority(
    *,
    subject,
    operation,
    evidence_identity: str,
) -> WorkflowAuthorityReference:
    return WorkflowAuthorityReference.create(
        authority_kind="local-reference-review-policy",
        subject_identity=subject,
        operation_identities=(operation,),
        evidence_identity=WorkflowExternalReferenceIdentity(evidence_identity),
        authority_version="1",
    )


def transition_to_manual_review(
    tmp_path: Path,
):
    selected = evidence()
    claim_candidate = candidate()
    workflow = ReferenceReviewWorkflow()
    started = workflow.start(selected)
    adapter = IngestionEvidenceReviewAdapter()
    transition_input = adapter.transition_input(
        started=started,
        evidence=selected,
        candidate=claim_candidate,
        actor_identity=WorkflowActorIdentity("operator:reviewer"),
        authority_reference=authority(
            subject=started.run.subject_identity,
            operation=REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION,
            evidence_identity="policy:reference-review:observe-fixture",
        ),
        idempotency_identity=WorkflowIdempotencyIdentity(
            "reference-review:fixture:observe"
        ),
    )
    runtime = LocalWorkflowRuntime(
        WorkflowRuntimeRepository(
            SQLiteAtomicRevisionStore(
                tmp_path / "private" / "reference-review.sqlite3"
            )
        )
    )
    assert runtime.start(started).status is WorkflowRuntimeActionStatus.RECORDED
    retained = runtime.retain_request(
        WorkflowTransitionPreflightInput(
            transition_input.definition,
            transition_input.run,
            transition_input.prior_state,
            transition_input.request,
        )
    )
    transitioned = runtime.record_transition(transition_input)
    assert retained.status is WorkflowRuntimeActionStatus.RECORDED
    assert transitioned.status is WorkflowRuntimeActionStatus.RECORDED
    assert transitioned.transition is not None
    outcome = transitioned.transition.outcome
    assert outcome.kind is WorkflowTransitionOutcomeKind.APPLIED
    assert outcome.successor_run is not None
    assert outcome.successor_state is not None
    return runtime, adapter, selected, claim_candidate, outcome


def test__ingestion_locator_fixture__maps_into_workflow_input() -> None:
    fixture_path = (
        Path(__file__).parent / "fixtures" / "ingestion-claim-candidate.json"
    )
    value = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert value.pop("fixture_schema") == (
        "projectkoios.workflow.ingestion-claim-candidate-fixture:1"
    )
    assert value.pop("producer_contract_id") == (
        "projectkoios.ingestion.reference-claim-candidate"
    )
    assert value.pop("producer_contract_version") == "0.1.0"
    value["matched_topic_anchor_identities"] = tuple(
        value["matched_topic_anchor_identities"]
    )
    claim_candidate = IngestionClaimCandidateReference.create(**value)
    selected = IngestionReferenceEvidenceReference.create(
        record_identity=claim_candidate.reference_evidence_record_identity,
        source_blob_identity=claim_candidate.source_blob_identity,
        source_sha256=claim_candidate.source_sha256,
        source_byte_length=123,
        source_media_type="application/pdf",
        extraction_artifact_sha256="c" * 64,
        transcript_artifact_sha256="d" * 64,
        audit_artifact_sha256="e" * 64,
    )
    started = ReferenceReviewWorkflow().start(selected)
    transition_input = IngestionEvidenceReviewAdapter().transition_input(
        started=started,
        evidence=selected,
        candidate=claim_candidate,
        actor_identity=WorkflowActorIdentity("operator:fixture"),
        authority_reference=authority(
            subject=started.run.subject_identity,
            operation=REQUIRE_MANUAL_CLAIM_REVIEW_OPERATION,
            evidence_identity="policy:ingestion-locator-fixture",
        ),
        idempotency_identity=WorkflowIdempotencyIdentity(
            "ingestion-locator-fixture:1"
        ),
    )

    assert any(
        reference.reference_identity.value == claim_candidate.identity.value
        for reference in transition_input.request.input_references
    )


def test__reference_review__requires_manual_review_for_claim_candidate(
    tmp_path: Path,
) -> None:
    _, _, selected, claim_candidate, outcome = transition_to_manual_review(
        tmp_path
    )

    assert {
        reference.reference_identity.value
        for reference in outcome.successor_state.state_references
    } == {
        selected.identity.value,
        claim_candidate.identity.value,
        ReferenceReviewStage.MANUAL_CLAIM_REVIEW_REQUIRED.value,
    }
    assert all(
        "authority" not in field.name
        for field in fields(IngestionClaimCandidateReference)
    )


@pytest.mark.parametrize(
    ("outcome_name", "operation", "stage"),
    (
        (
            ReferenceReviewStage.REVIEWED_RETAINED.value,
            RETAIN_REVIEWED_CLAIM_OPERATION,
            ReferenceReviewStage.REVIEWED_RETAINED,
        ),
        (
            ReferenceReviewStage.REVIEWED_EXCLUDED.value,
            EXCLUDE_REVIEWED_CLAIM_OPERATION,
            ReferenceReviewStage.REVIEWED_EXCLUDED,
        ),
    ),
)
def test__reference_review__records_exact_human_decision_without_publication(
    tmp_path: Path,
    outcome_name: str,
    operation,
    stage: ReferenceReviewStage,
) -> None:
    runtime, adapter, selected, claim_candidate, first = (
        transition_to_manual_review(tmp_path)
    )
    assert first.successor_run is not None
    assert first.successor_state is not None
    decision = WorkflowDecisionReference.create(
        decision_kind="manual-reference-claim-review",
        scope=claim_candidate.candidate_identity,
        subject_identity=first.successor_run.subject_identity,
        authority_identity=WorkflowExternalReferenceIdentity(
            "operator:claim-review-board"
        ),
        outcome=outcome_name,
        evidence_identity=WorkflowExternalReferenceIdentity(
            f"decision-evidence:{outcome_name}"
        ),
        decision_version="1",
    )
    transition_input = adapter.decision_transition_input(
        run=first.successor_run,
        state=first.successor_state,
        evidence=selected,
        candidate=claim_candidate,
        decision=decision,
        actor_identity=WorkflowActorIdentity("operator:reviewer"),
        authority_reference=authority(
            subject=first.successor_run.subject_identity,
            operation=operation,
            evidence_identity=f"policy:reference-review:{outcome_name}",
        ),
        idempotency_identity=WorkflowIdempotencyIdentity(
            f"reference-review:fixture:{outcome_name}"
        ),
    )
    retained = runtime.retain_request(
        WorkflowTransitionPreflightInput(
            transition_input.definition,
            transition_input.run,
            transition_input.prior_state,
            transition_input.request,
        )
    )
    transitioned = runtime.record_transition(transition_input)

    assert retained.status is WorkflowRuntimeActionStatus.RECORDED
    assert transitioned.status is WorkflowRuntimeActionStatus.RECORDED
    assert transitioned.transition is not None
    final = transitioned.transition.outcome
    assert final.kind is WorkflowTransitionOutcomeKind.APPLIED
    assert final.successor_run is not None
    assert final.successor_state is not None
    assert final.successor_run.status is WorkflowRunStatus.COMPLETED
    assert final.successor_run.decision_references == (decision,)
    assert {
        reference.reference_identity.value
        for reference in final.successor_state.state_references
    } == {
        selected.identity.value,
        claim_candidate.identity.value,
        stage.value,
    }


def test__reference_review__admits_no_support_or_publication() -> None:
    definition = ReferenceReviewWorkflow().definition
    operations = {
        operation.value for operation in definition.operation_identities
    }

    assert operations == {
        "exclude-reviewed-claim",
        "require-manual-claim-review",
        "retain-reviewed-claim",
    }
    assert "published" not in {stage.value for stage in ReferenceReviewStage}
    assert not any(
        word in operation
        for operation in operations
        for word in ("accept", "claim-support", "publish")
    )


def test__ingestion_inputs__are_exact_and_fail_closed() -> None:
    selected = evidence()
    claim_candidate = candidate()

    assert evidence() == selected
    assert candidate() == claim_candidate
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
    with pytest.raises(ValueError, match="incomplete"):
        replace(claim_candidate, limitations=("manual_claim_review_required",))
    with pytest.raises(ValueError, match="inconsistent"):
        replace(claim_candidate, page_text_sha256="f" * 64)


def test__reference_review__requires_operation_specific_authority(
    tmp_path: Path,
) -> None:
    runtime, adapter, selected, claim_candidate, first = (
        transition_to_manual_review(tmp_path)
    )
    assert first.successor_run is not None
    assert first.successor_state is not None
    decision = WorkflowDecisionReference.create(
        decision_kind="manual-reference-claim-review",
        scope=claim_candidate.candidate_identity,
        subject_identity=first.successor_run.subject_identity,
        authority_identity=WorkflowExternalReferenceIdentity(
            "operator:claim-review-board"
        ),
        outcome=ReferenceReviewStage.REVIEWED_RETAINED.value,
        evidence_identity=WorkflowExternalReferenceIdentity(
            "decision-evidence:retain"
        ),
        decision_version="1",
    )
    transition_input = adapter.decision_transition_input(
        run=first.successor_run,
        state=first.successor_state,
        evidence=selected,
        candidate=claim_candidate,
        decision=decision,
        actor_identity=WorkflowActorIdentity("operator:reviewer"),
        authority_reference=authority(
            subject=first.successor_run.subject_identity,
            operation=EXCLUDE_REVIEWED_CLAIM_OPERATION,
            evidence_identity="policy:reference-review:exclude-only",
        ),
        idempotency_identity=WorkflowIdempotencyIdentity(
            "reference-review:fixture:wrong-authority"
        ),
    )

    result = runtime.retain_request(
        WorkflowTransitionPreflightInput(
            transition_input.definition,
            transition_input.run,
            transition_input.prior_state,
            transition_input.request,
        )
    )

    assert result.status is WorkflowRuntimeActionStatus.REJECTED
    assert result.validation is not None
    assert {finding.code.value for finding in result.validation.findings} == {
        "authority_scope_mismatch"
    }


def test__reference_review__rejects_wrong_decision_scope(
    tmp_path: Path,
) -> None:
    _, adapter, selected, claim_candidate, first = transition_to_manual_review(
        tmp_path
    )
    assert first.successor_run is not None
    assert first.successor_state is not None
    decision = WorkflowDecisionReference.create(
        decision_kind="manual-reference-claim-review",
        scope=f"reference-claim-candidate:sha256:{'9' * 64}",
        subject_identity=first.successor_run.subject_identity,
        authority_identity=WorkflowExternalReferenceIdentity(
            "operator:claim-review-board"
        ),
        outcome=ReferenceReviewStage.REVIEWED_RETAINED.value,
        evidence_identity=WorkflowExternalReferenceIdentity(
            "decision-evidence:wrong-scope"
        ),
        decision_version="1",
    )

    with pytest.raises(ValueError, match="review contract"):
        adapter.decision_transition_input(
            run=first.successor_run,
            state=first.successor_state,
            evidence=selected,
            candidate=claim_candidate,
            decision=decision,
            actor_identity=WorkflowActorIdentity("operator:reviewer"),
            authority_reference=authority(
                subject=first.successor_run.subject_identity,
                operation=RETAIN_REVIEWED_CLAIM_OPERATION,
                evidence_identity="policy:reference-review:retain",
            ),
            idempotency_identity=WorkflowIdempotencyIdentity(
                "reference-review:fixture:wrong-scope"
            ),
        )
