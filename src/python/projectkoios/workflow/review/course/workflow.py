"""Pure metadata-only course-review workflow and organizer input adapter."""

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

from .models import CourseReviewStage, OrganizerTeachingProposalReference

COURSE_REVIEW_CONTRACT_ID = "projectkoios.course-review"
COURSE_REVIEW_CONTRACT_VERSION = "0.1.0"
COURSE_IDENTITY_CANDIDATE_OPERATION = WorkflowOperationIdentity(
    "record-course-identity-candidate"
)
_OPERATIONS = (COURSE_IDENTITY_CANDIDATE_OPERATION,)
_DEFINITION_DIGEST = hashlib.sha256(
    json.dumps(
        {
            "contract_id": COURSE_REVIEW_CONTRACT_ID,
            "contract_version": COURSE_REVIEW_CONTRACT_VERSION,
            "stages": [stage.value for stage in CourseReviewStage],
            "operations": [operation.value for operation in _OPERATIONS],
            "publication_operation": None,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
).hexdigest()


def _definition() -> WorkflowDefinitionReference:
    return WorkflowDefinitionReference.create(
        contract_id=COURSE_REVIEW_CONTRACT_ID,
        definition_version=COURSE_REVIEW_CONTRACT_VERSION,
        definition_digest_sha256=_DEFINITION_DIGEST,
        operation_identities=_OPERATIONS,
    )


def _stage_reference(stage: CourseReviewStage) -> WorkflowTypedReference:
    return WorkflowTypedReference(
        "course-review-stage",
        WorkflowExternalReferenceIdentity(stage.value),
    )


def _proposal_reference(
    proposal: OrganizerTeachingProposalReference,
) -> WorkflowTypedReference:
    return WorkflowTypedReference(
        "organizer-teaching-proposal",
        WorkflowExternalReferenceIdentity(proposal.identity.value),
    )


class CourseReviewWorkflow:
    """Start local metadata-only review runs from typed organizer proposals."""

    @property
    def definition(self) -> WorkflowDefinitionReference:
        """Return the immutable course-review definition reference."""
        return _definition()

    def start(
        self,
        proposal: OrganizerTeachingProposalReference,
    ) -> WorkflowRunStartResult:
        """Create a revision-zero run without granting review authority."""
        if type(proposal) is not OrganizerTeachingProposalReference:
            raise TypeError(
                "proposal must be OrganizerTeachingProposalReference"
            )
        return WorkflowRunStarter().execute(
            definition=self.definition,
            subject_identity=WorkflowSubjectIdentity(
                f"course:{proposal.course_identity}"
            ),
            run_key=f"course-review:{proposal.course_identity}",
            initial_state_references=(
                _stage_reference(CourseReviewStage.PROPOSAL_OBSERVED),
                _proposal_reference(proposal),
            ),
        )


class OrganizerCourseCandidateAdapter:
    """Convert one teaching proposal into pure candidate transition evidence."""

    def transition_input(
        self,
        *,
        started: WorkflowRunStartResult,
        proposal: OrganizerTeachingProposalReference,
        actor_identity: WorkflowActorIdentity,
        authority_reference: WorkflowAuthorityReference,
        idempotency_identity: WorkflowIdempotencyIdentity,
    ) -> WorkflowTransitionInput:
        """Return core input without payload read, policy grant, or effect."""
        if type(started) is not WorkflowRunStartResult:
            raise TypeError("started must be WorkflowRunStartResult")
        if type(proposal) is not OrganizerTeachingProposalReference:
            raise TypeError(
                "proposal must be OrganizerTeachingProposalReference"
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
        if started.run.subject_identity != WorkflowSubjectIdentity(
            f"course:{proposal.course_identity}"
        ):
            raise ValueError("proposal course does not match the run subject")
        expected_state = (
            _stage_reference(CourseReviewStage.PROPOSAL_OBSERVED),
            _proposal_reference(proposal),
        )
        if started.state.state_references != expected_state:
            raise ValueError("run is not at the exact proposal-observed state")
        request = WorkflowTransitionRequest.create(
            run_identity=started.run.identity,
            expected_prior_state_identity=started.state.identity,
            expected_revision=started.run.revision,
            operation_identity=COURSE_IDENTITY_CANDIDATE_OPERATION,
            input_references=(
                WorkflowTypedReference(
                    "course-catalog-revision",
                    WorkflowExternalReferenceIdentity(
                        proposal.catalog_revision
                    ),
                ),
                WorkflowTypedReference(
                    "organizer-model",
                    WorkflowExternalReferenceIdentity(proposal.model_identity),
                ),
                WorkflowTypedReference(
                    "organizer-proposal-set",
                    WorkflowExternalReferenceIdentity(
                        proposal.proposal_set_identity
                    ),
                ),
                _proposal_reference(proposal),
                WorkflowTypedReference(
                    "source-metadata",
                    WorkflowExternalReferenceIdentity(
                        f"sha256:{proposal.source_metadata_sha256}"
                    ),
                    proposal.source_metadata_sha256,
                ),
            ),
            artifact_references=(),
            decision_references=(),
            actor_identity=actor_identity,
            authority_reference=authority_reference,
            idempotency_identity=idempotency_identity,
        )
        evidence = WorkflowAdapterEvidence.create(
            adapter_identity=WorkflowAdapterIdentity(
                "organizer-course-candidate:0.1.0"
            ),
            definition_identity=definition.identity,
            request_identity=request.identity,
            prior_state_identity=started.state.identity,
            disposition=WorkflowAdapterDisposition.ENABLED,
            successor_state_references=(
                _stage_reference(CourseReviewStage.COURSE_IDENTITY_CANDIDATE),
                _proposal_reference(proposal),
            ),
            successor_run_status=started.run.status,
            reasons=("organizer metadata retained as non-authorizing input",),
        )
        return WorkflowTransitionInput(
            definition,
            started.run,
            started.state,
            request,
            evidence,
        )
