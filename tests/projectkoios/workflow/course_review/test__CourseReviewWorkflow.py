"""Verification for typed organizer input and local course-review workflow."""

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
from projectkoios.workflow.course_review import (
    COURSE_IDENTITY_CANDIDATE_OPERATION,
    CourseReviewStage,
    CourseReviewWorkflow,
    OrganizerCourseCandidateAdapter,
    OrganizerTeachingProposalReference,
)
from projectkoios.workflow.persistence import SQLiteAtomicRevisionStore
from projectkoios.workflow.runtime import (
    LocalWorkflowRuntime,
    WorkflowRuntimeActionStatus,
    WorkflowRuntimeRepository,
)


def proposal() -> OrganizerTeachingProposalReference:
    return OrganizerTeachingProposalReference.create(
        proposal_identity="proposal:ENGR219:1",
        proposal_set_identity="proposal-set:teaching:1",
        model_identity="ollama:model:sha256:fixture",
        catalog_revision="course-catalog:7bd6ce7",
        course_identity="pacific_ENGR219",
        source_metadata_sha256="a" * 64,
    )


def test__course_review__retains_organizer_input_without_granting_authority(
    tmp_path: Path,
) -> None:
    selected = proposal()
    workflow = CourseReviewWorkflow()
    started = workflow.start(selected)
    authority = WorkflowAuthorityReference.create(
        authority_kind="local-course-review-policy",
        subject_identity=started.run.subject_identity,
        operation_identities=(COURSE_IDENTITY_CANDIDATE_OPERATION,),
        evidence_identity=WorkflowExternalReferenceIdentity(
            "policy:course-review:fixture"
        ),
        authority_version="1",
    )
    transition_input = OrganizerCourseCandidateAdapter().transition_input(
        started=started,
        proposal=selected,
        actor_identity=WorkflowActorIdentity("agent:organizer"),
        authority_reference=authority,
        idempotency_identity=WorkflowIdempotencyIdentity(
            "course-candidate:ENGR219:1"
        ),
    )
    runtime = LocalWorkflowRuntime(
        WorkflowRuntimeRepository(
            SQLiteAtomicRevisionStore(
                tmp_path / "private" / "course-review.sqlite3"
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
    assert (
        transitioned.transition.outcome.successor_state.state_references[
            0
        ].reference_identity.value
        == CourseReviewStage.COURSE_IDENTITY_CANDIDATE.value
    )
    assert transition_input.request.authority_reference == authority
    assert all(
        "authority" not in field.name
        for field in fields(OrganizerTeachingProposalReference)
    )


def test__course_review__definition_excludes_publication_operation() -> None:
    definition = CourseReviewWorkflow().definition

    assert definition.operation_identities == (
        COURSE_IDENTITY_CANDIDATE_OPERATION,
    )
    assert "publish" not in {
        operation.value for operation in definition.operation_identities
    }
    assert "published" not in {stage.value for stage in CourseReviewStage}
    assert tuple(stage.value for stage in CourseReviewStage)[-2:] == (
        "reviewed_retained",
        "reviewed_excluded",
    )


@pytest.mark.parametrize(
    "proposal_identity",
    (
        "/Users/operator/private/proposal",
        "private/course/proposal.json",
        "proposal\nsecret",
    ),
)
def test__organizer_proposal__rejects_paths_and_controls(
    proposal_identity: str,
) -> None:
    with pytest.raises(ValueError, match="compact non-path"):
        OrganizerTeachingProposalReference.create(
            proposal_identity=proposal_identity,
            proposal_set_identity="proposal-set:1",
            model_identity="model:1",
            catalog_revision="catalog:1",
            course_identity="pacific_ENGR219",
            source_metadata_sha256="a" * 64,
        )


def test__organizer_proposal__is_content_identified_and_teaching_only() -> None:
    selected = proposal()

    assert proposal() == selected
    with pytest.raises(ValueError, match="life_domain"):
        replace(selected, life_domain="research")
    with pytest.raises(ValueError, match="inconsistent"):
        replace(
            selected,
            source_metadata_sha256="b" * 64,
        )
