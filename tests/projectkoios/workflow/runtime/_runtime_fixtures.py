"""Synthetic payload-free fixtures for the local workflow runtime."""

from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True, slots=True)
class RuntimeFixture:
    definition: WorkflowDefinitionReference
    operation: WorkflowOperationIdentity
    authority: WorkflowAuthorityReference
    started: WorkflowRunStartResult


def runtime_fixture() -> RuntimeFixture:
    operation = WorkflowOperationIdentity("record-course-candidate")
    definition = WorkflowDefinitionReference.create(
        contract_id="projectkoios.course-review",
        definition_version="1",
        definition_digest_sha256="a" * 64,
        operation_identities=(operation,),
    )
    subject = WorkflowSubjectIdentity("course:pacific_ENGR219")
    started = WorkflowRunStarter().execute(
        definition=definition,
        subject_identity=subject,
        run_key="course-review:pacific_ENGR219",
        initial_state_references=(
            WorkflowTypedReference(
                "course-review-status",
                WorkflowExternalReferenceIdentity("inventory-only"),
            ),
        ),
    )
    authority = WorkflowAuthorityReference.create(
        authority_kind="local-course-review-policy",
        subject_identity=subject,
        operation_identities=(operation,),
        evidence_identity=WorkflowExternalReferenceIdentity(
            "policy:course-review:1"
        ),
        authority_version="1",
    )
    return RuntimeFixture(definition, operation, authority, started)


def transition_input(
    fixture: RuntimeFixture,
    *,
    request_key: str = "candidate:1",
    expected_revision: int = 0,
    proposal_identity: str = "proposal-set:sha256:fixture",
) -> WorkflowTransitionInput:
    request = WorkflowTransitionRequest.create(
        run_identity=fixture.started.run.identity,
        expected_prior_state_identity=fixture.started.state.identity,
        expected_revision=expected_revision,
        operation_identity=fixture.operation,
        input_references=(
            WorkflowTypedReference(
                "organizer-proposal-set",
                WorkflowExternalReferenceIdentity(proposal_identity),
                "b" * 64,
            ),
        ),
        artifact_references=(),
        decision_references=(),
        actor_identity=WorkflowActorIdentity("agent:organizer"),
        authority_reference=fixture.authority,
        idempotency_identity=WorkflowIdempotencyIdentity(request_key),
    )
    evidence = WorkflowAdapterEvidence.create(
        adapter_identity=WorkflowAdapterIdentity("course-review-baseline:1"),
        definition_identity=fixture.definition.identity,
        request_identity=request.identity,
        prior_state_identity=fixture.started.state.identity,
        disposition=WorkflowAdapterDisposition.ENABLED,
        successor_state_references=(
            WorkflowTypedReference(
                "course-review-status",
                WorkflowExternalReferenceIdentity("manual-review-required"),
            ),
        ),
        successor_run_status=fixture.started.run.status,
        reasons=("metadata candidate requires manual review",),
    )
    return WorkflowTransitionInput(
        fixture.definition,
        fixture.started.run,
        fixture.started.state,
        request,
        evidence,
    )
