"""Synthetic fixtures for Petri-independent workflow-core verification."""

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
    WorkflowRun,
    WorkflowRunStarter,
    WorkflowStateSnapshot,
    WorkflowSubjectIdentity,
    WorkflowTransitionInput,
    WorkflowTransitionRequest,
    WorkflowTypedReference,
)

_DIGEST = "a" * 64


@dataclass(frozen=True)
class CoreFixture:
    """Minimal valid workflow transition fixture."""

    definition: WorkflowDefinitionReference
    operation: WorkflowOperationIdentity
    subject: WorkflowSubjectIdentity
    run: WorkflowRun
    state: WorkflowStateSnapshot
    authority: WorkflowAuthorityReference


def core_fixture() -> CoreFixture:
    """Return a valid revision-zero synthetic extraction run."""
    operation = WorkflowOperationIdentity("extract")
    definition = WorkflowDefinitionReference.create(
        contract_id="test.workflow",
        definition_version="1",
        definition_digest_sha256=_DIGEST,
        operation_identities=(operation,),
    )
    subject = WorkflowSubjectIdentity("source:sha256:test")
    start = WorkflowRunStarter().execute(
        definition=definition,
        subject_identity=subject,
        run_key="test-run",
        initial_state_references=(
            WorkflowTypedReference(
                "stage",
                WorkflowExternalReferenceIdentity("acquired"),
            ),
        ),
    )
    authority = WorkflowAuthorityReference.create(
        authority_kind="test-policy",
        subject_identity=subject,
        operation_identities=(operation,),
        evidence_identity=WorkflowExternalReferenceIdentity("policy:test"),
        authority_version="1",
    )
    return CoreFixture(
        definition,
        operation,
        subject,
        start.run,
        start.state,
        authority,
    )


def transition_input(
    fixture: CoreFixture,
    *,
    disposition: WorkflowAdapterDisposition = (
        WorkflowAdapterDisposition.ENABLED
    ),
    expected_revision: int | None = None,
    authority: WorkflowAuthorityReference | None = None,
) -> WorkflowTransitionInput:
    """Return a transition input with exact adapter evidence."""
    request = WorkflowTransitionRequest.create(
        run_identity=fixture.run.identity,
        expected_prior_state_identity=fixture.state.identity,
        expected_revision=(
            fixture.run.revision
            if expected_revision is None
            else expected_revision
        ),
        operation_identity=fixture.operation,
        input_references=(),
        artifact_references=(),
        decision_references=(),
        actor_identity=WorkflowActorIdentity("operator:test"),
        authority_reference=authority or fixture.authority,
        idempotency_identity=WorkflowIdempotencyIdentity("request:test"),
    )
    enabled = disposition is WorkflowAdapterDisposition.ENABLED
    evidence = WorkflowAdapterEvidence.create(
        adapter_identity=WorkflowAdapterIdentity("baseline:test"),
        definition_identity=fixture.definition.identity,
        request_identity=request.identity,
        prior_state_identity=fixture.state.identity,
        disposition=disposition,
        successor_state_references=(
            (
                WorkflowTypedReference(
                    "stage",
                    WorkflowExternalReferenceIdentity("extracted"),
                ),
            )
            if enabled
            else ()
        ),
        successor_run_status=fixture.run.status if enabled else None,
        reasons=() if enabled else ("synthetic adapter disposition",),
    )
    return WorkflowTransitionInput(
        fixture.definition,
        fixture.run,
        fixture.state,
        request,
        evidence,
    )
