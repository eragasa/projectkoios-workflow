"""Verification for pure workflow transition processing and replay."""

from __future__ import annotations

from dataclasses import replace

import pytest
from _core_fixtures import core_fixture, transition_input
from projectkoios.workflow.core import (
    WorkflowActorIdentity,
    WorkflowAdapterDisposition,
    WorkflowAdapterEvidence,
    WorkflowAdapterIdentity,
    WorkflowArtifactDisposition,
    WorkflowArtifactReference,
    WorkflowAuditEvent,
    WorkflowAuditReference,
    WorkflowAuthorityReference,
    WorkflowDecisionReference,
    WorkflowExternalReferenceIdentity,
    WorkflowIdempotencyIdentity,
    WorkflowInfrastructureFailureEvidence,
    WorkflowOperationIdentity,
    WorkflowRequestBounds,
    WorkflowRunIdentity,
    WorkflowRunStarter,
    WorkflowRunStatus,
    WorkflowSubjectIdentity,
    WorkflowTransitionExecution,
    WorkflowTransitionInput,
    WorkflowTransitionOutcomeKind,
    WorkflowTransitionPreflightInput,
    WorkflowTransitionProcessor,
    WorkflowTransitionReplayer,
    WorkflowTransitionRequest,
    WorkflowTransitionValidator,
    WorkflowTypedReference,
    WorkflowValidationFindingCode,
)


def test__transition_validator__preflights_without_adapter_evidence() -> None:
    """A valid request can be checked before any adapter is invoked."""
    fixture = core_fixture()
    transition = transition_input(fixture)
    preflight = WorkflowTransitionPreflightInput(
        fixture.definition,
        fixture.run,
        fixture.state,
        transition.request,
    )

    validation = WorkflowTransitionValidator().execute(preflight)

    assert validation.is_valid
    assert fixture.run.revision == 0
    assert fixture.run.current_state_identity == fixture.state.identity


def test__transition_validator__matches_processor_base_findings() -> None:
    """Preflight and final processing share exact structural validation."""
    fixture = core_fixture()
    transition = transition_input(fixture, expected_revision=1)
    preflight = WorkflowTransitionPreflightInput(
        fixture.definition,
        fixture.run,
        fixture.state,
        transition.request,
    )

    validation = WorkflowTransitionValidator().execute(preflight)
    execution = WorkflowTransitionProcessor().execute(transition)

    assert validation == execution.outcome.validation
    assert {finding.code for finding in validation.findings} == {
        WorkflowValidationFindingCode.REVISION_CONFLICT
    }


def test__transition_validator__rejects_unknown_operation_before_dispatch() -> (
    None
):
    """An operation absent from the definition fails before adapter work."""
    fixture = core_fixture()
    operation = WorkflowOperationIdentity("unknown")
    authority = WorkflowAuthorityReference.create(
        authority_kind="test-policy",
        subject_identity=fixture.subject,
        operation_identities=(operation,),
        evidence_identity=WorkflowExternalReferenceIdentity("policy:unknown"),
        authority_version="1",
    )
    request = WorkflowTransitionRequest.create(
        run_identity=fixture.run.identity,
        expected_prior_state_identity=fixture.state.identity,
        expected_revision=fixture.run.revision,
        operation_identity=operation,
        input_references=(),
        artifact_references=(),
        decision_references=(),
        actor_identity=WorkflowActorIdentity("operator:test"),
        authority_reference=authority,
        idempotency_identity=WorkflowIdempotencyIdentity("request:unknown"),
    )

    validation = WorkflowTransitionValidator().execute(
        WorkflowTransitionPreflightInput(
            fixture.definition,
            fixture.run,
            fixture.state,
            request,
        )
    )

    assert {finding.code for finding in validation.findings} == {
        WorkflowValidationFindingCode.UNKNOWN_OPERATION
    }


def test__transition_validator__checks_structural_authority_binding() -> None:
    """Preflight checks authority scope without authenticating its evidence."""
    fixture = core_fixture()
    other_operation = WorkflowOperationIdentity("other")
    authority = WorkflowAuthorityReference.create(
        authority_kind="externally-verified-policy",
        subject_identity=fixture.subject,
        operation_identities=(other_operation,),
        evidence_identity=WorkflowExternalReferenceIdentity(
            "authority-attestation:test"
        ),
        authority_version="1",
    )
    request = WorkflowTransitionRequest.create(
        run_identity=fixture.run.identity,
        expected_prior_state_identity=fixture.state.identity,
        expected_revision=fixture.run.revision,
        operation_identity=fixture.operation,
        input_references=(),
        artifact_references=(),
        decision_references=(),
        actor_identity=WorkflowActorIdentity("operator:test"),
        authority_reference=authority,
        idempotency_identity=WorkflowIdempotencyIdentity(
            "request:authority-scope"
        ),
    )

    validation = WorkflowTransitionValidator().execute(
        WorkflowTransitionPreflightInput(
            fixture.definition,
            fixture.run,
            fixture.state,
            request,
        )
    )

    assert {finding.code for finding in validation.findings} == {
        WorkflowValidationFindingCode.AUTHORITY_SCOPE_MISMATCH
    }


def test__transition_validator__requires_exact_preflight_type() -> None:
    """The public validator fails closed on an accidental final input."""
    fixture = core_fixture()
    transition = transition_input(fixture)

    with pytest.raises(TypeError, match="WorkflowTransitionPreflightInput"):
        WorkflowTransitionValidator().execute(transition)  # type: ignore[arg-type]


def test__transition_processor__applies_enabled_successor_immutably() -> None:
    """An enabled result creates revision one without mutating revision zero."""
    fixture = core_fixture()
    transition = transition_input(fixture)

    execution = WorkflowTransitionProcessor().execute(transition)

    assert execution.outcome.kind is WorkflowTransitionOutcomeKind.APPLIED
    assert execution.outcome.validation.is_valid
    assert execution.outcome.successor_run is not None
    assert execution.outcome.successor_state is not None
    assert execution.outcome.successor_run.identity == fixture.run.identity
    assert execution.outcome.successor_run.revision == 1
    assert execution.outcome.successor_state.revision == 1
    assert execution.outcome.successor_state.predecessor_state_identity == (
        fixture.state.identity
    )
    assert fixture.run.revision == 0
    assert fixture.state.predecessor_state_identity is None
    assert execution.audit_event.event_kind == "transition.applied"


def test__transition_replayer__recomputes_identical_execution() -> None:
    """Exact immutable inputs reproduce the same outcome and audit."""
    fixture = core_fixture()
    transition = transition_input(fixture)
    execution = WorkflowTransitionProcessor().execute(transition)

    replay = WorkflowTransitionReplayer().execute(transition, execution)

    assert replay.matches
    assert replay.expected_outcome_identity == replay.replayed_outcome_identity
    assert replay.expected_audit_identity == replay.replayed_audit_identity


def test__transition_processor__reports_expected_revision_conflict() -> None:
    """A stale expected revision is a conflict and creates no successor."""
    fixture = core_fixture()
    transition = transition_input(fixture, expected_revision=1)

    execution = WorkflowTransitionProcessor().execute(transition)

    assert execution.outcome.kind is WorkflowTransitionOutcomeKind.CONFLICT
    assert execution.outcome.successor_run is None
    assert execution.outcome.successor_state is None
    assert {item.code for item in execution.outcome.validation.findings} == {
        WorkflowValidationFindingCode.REVISION_CONFLICT
    }


def test__transition_processor__rejects_out_of_scope_authority() -> None:
    """Subject-specific authority cannot authorize a different subject's run."""
    fixture = core_fixture()
    wrong_authority = WorkflowAuthorityReference.create(
        authority_kind="test-policy",
        subject_identity=type(fixture.subject)("source:other"),
        operation_identities=(fixture.operation,),
        evidence_identity=WorkflowExternalReferenceIdentity("policy:other"),
        authority_version="1",
    )
    transition = transition_input(fixture, authority=wrong_authority)

    execution = WorkflowTransitionProcessor().execute(transition)

    assert (
        execution.outcome.kind is WorkflowTransitionOutcomeKind.REJECTED_INVALID
    )
    assert WorkflowValidationFindingCode.AUTHORITY_SUBJECT_MISMATCH in {
        item.code for item in execution.outcome.validation.findings
    }


@pytest.mark.parametrize(
    ("disposition", "expected_kind"),
    (
        (
            WorkflowAdapterDisposition.NOT_ENABLED,
            WorkflowTransitionOutcomeKind.NOT_ENABLED,
        ),
        (
            WorkflowAdapterDisposition.BLOCKED,
            WorkflowTransitionOutcomeKind.BLOCKED,
        ),
    ),
)
def test__transition_processor__does_not_fire_disabled_action(
    disposition: WorkflowAdapterDisposition,
    expected_kind: WorkflowTransitionOutcomeKind,
) -> None:
    """A non-enabled adapter disposition never produces successor state."""
    fixture = core_fixture()
    transition = transition_input(fixture, disposition=disposition)

    execution = WorkflowTransitionProcessor().execute(transition)

    assert execution.outcome.kind is expected_kind
    assert execution.outcome.successor_state is None
    assert execution.outcome.successor_run is None


def test__transition_processor__separates_infrastructure_failure() -> None:
    """Infrastructure failure is neither invalid input nor domain rejection."""
    fixture = core_fixture()
    adapter_transition = transition_input(fixture)
    failure = WorkflowInfrastructureFailureEvidence.create(
        request_identity=adapter_transition.request.identity,
        operation_phase="adapter-dispatch",
        failure_code="worker-unavailable",
        message="synthetic worker unavailable",
        evidence_identity=WorkflowExternalReferenceIdentity("failure-log:test"),
    )
    transition = WorkflowTransitionInput(
        fixture.definition,
        fixture.run,
        fixture.state,
        adapter_transition.request,
        infrastructure_failure=failure,
    )

    execution = WorkflowTransitionProcessor().execute(transition)

    assert (
        execution.outcome.kind
        is WorkflowTransitionOutcomeKind.INFRASTRUCTURE_FAILURE
    )
    assert execution.outcome.validation.is_valid
    assert execution.outcome.successor_run is None
    assert execution.outcome.infrastructure_failure_identity == failure.identity


def test__transition_processor__closes_mismatched_failure_evidence() -> None:
    """Mismatched infrastructure evidence produces an audited rejection."""
    fixture = core_fixture()
    adapter_transition = transition_input(fixture)
    other_request = WorkflowTransitionRequest.create(
        run_identity=fixture.run.identity,
        expected_prior_state_identity=fixture.state.identity,
        expected_revision=fixture.run.revision,
        operation_identity=fixture.operation,
        input_references=(),
        artifact_references=(),
        decision_references=(),
        actor_identity=WorkflowActorIdentity("operator:test"),
        authority_reference=fixture.authority,
        idempotency_identity=WorkflowIdempotencyIdentity(
            "request:other-failure"
        ),
    )
    failure = WorkflowInfrastructureFailureEvidence.create(
        request_identity=other_request.identity,
        operation_phase="adapter-dispatch",
        failure_code="worker-unavailable",
        message="synthetic mismatched failure",
        evidence_identity=WorkflowExternalReferenceIdentity(
            "failure-log:mismatched"
        ),
    )

    execution = WorkflowTransitionProcessor().execute(
        WorkflowTransitionInput(
            fixture.definition,
            fixture.run,
            fixture.state,
            adapter_transition.request,
            infrastructure_failure=failure,
        )
    )

    assert (
        execution.outcome.kind is WorkflowTransitionOutcomeKind.REJECTED_INVALID
    )
    assert execution.outcome.infrastructure_failure_identity == failure.identity
    assert WorkflowValidationFindingCode.INFRASTRUCTURE_EVIDENCE_MISMATCH in {
        item.code for item in execution.outcome.validation.findings
    }


def test__transition_processor__rejects_mismatched_adapter_evidence() -> None:
    """Adapter evidence must bind the exact request and prior state."""
    fixture = core_fixture()
    transition = transition_input(fixture)
    assert transition.adapter_evidence is not None
    other_request = WorkflowTransitionRequest.create(
        run_identity=fixture.run.identity,
        expected_prior_state_identity=fixture.state.identity,
        expected_revision=fixture.run.revision,
        operation_identity=fixture.operation,
        input_references=(),
        artifact_references=(),
        decision_references=(),
        actor_identity=WorkflowActorIdentity("operator:test"),
        authority_reference=fixture.authority,
        idempotency_identity=WorkflowIdempotencyIdentity("request:other"),
    )
    other_evidence = WorkflowAdapterEvidence.create(
        adapter_identity=transition.adapter_evidence.adapter_identity,
        definition_identity=fixture.definition.identity,
        request_identity=other_request.identity,
        prior_state_identity=fixture.state.identity,
        disposition=WorkflowAdapterDisposition.ENABLED,
        successor_state_references=(
            WorkflowTypedReference(
                "stage",
                WorkflowExternalReferenceIdentity("extracted"),
            ),
        ),
        successor_run_status=WorkflowRunStatus.ACTIVE,
    )

    execution = WorkflowTransitionProcessor().execute(
        replace(transition, adapter_evidence=other_evidence)
    )

    assert (
        execution.outcome.kind is WorkflowTransitionOutcomeKind.REJECTED_INVALID
    )
    assert WorkflowValidationFindingCode.ADAPTER_EVIDENCE_MISMATCH in {
        item.code for item in execution.outcome.validation.findings
    }


def test__transition_processor__rejects_later_action_on_terminal_run() -> None:
    """A completed run cannot acquire another successor revision."""
    fixture = core_fixture()
    first_input = transition_input(fixture)
    assert first_input.adapter_evidence is not None
    completing_evidence = WorkflowAdapterEvidence.create(
        adapter_identity=WorkflowAdapterIdentity("baseline:test"),
        definition_identity=fixture.definition.identity,
        request_identity=first_input.request.identity,
        prior_state_identity=fixture.state.identity,
        disposition=WorkflowAdapterDisposition.ENABLED,
        successor_state_references=(
            WorkflowTypedReference(
                "stage",
                WorkflowExternalReferenceIdentity("completed"),
            ),
        ),
        successor_run_status=WorkflowRunStatus.COMPLETED,
        reasons=("synthetic completion",),
    )
    first = WorkflowTransitionProcessor().execute(
        replace(first_input, adapter_evidence=completing_evidence)
    )
    assert first.outcome.successor_run is not None
    assert first.outcome.successor_state is not None
    terminal_run = first.outcome.successor_run
    terminal_state = first.outcome.successor_state
    assert terminal_run.status_reasons == ("synthetic completion",)
    request = WorkflowTransitionRequest.create(
        run_identity=terminal_run.identity,
        expected_prior_state_identity=terminal_state.identity,
        expected_revision=terminal_run.revision,
        operation_identity=fixture.operation,
        input_references=(),
        artifact_references=(),
        decision_references=(),
        actor_identity=WorkflowActorIdentity("operator:test"),
        authority_reference=fixture.authority,
        idempotency_identity=WorkflowIdempotencyIdentity(
            "request:after-terminal"
        ),
    )
    evidence = WorkflowAdapterEvidence.create(
        adapter_identity=WorkflowAdapterIdentity("baseline:test"),
        definition_identity=fixture.definition.identity,
        request_identity=request.identity,
        prior_state_identity=terminal_state.identity,
        disposition=WorkflowAdapterDisposition.ENABLED,
        successor_state_references=terminal_state.state_references,
        successor_run_status=WorkflowRunStatus.COMPLETED,
        reasons=("already complete",),
    )

    execution = WorkflowTransitionProcessor().execute(
        WorkflowTransitionInput(
            fixture.definition,
            terminal_run,
            terminal_state,
            request,
            evidence,
        )
    )

    assert (
        execution.outcome.kind is WorkflowTransitionOutcomeKind.REJECTED_INVALID
    )
    assert WorkflowValidationFindingCode.TERMINAL_RUN in {
        item.code for item in execution.outcome.validation.findings
    }


def test__transition_processor__closes_successor_aggregate_overflow() -> None:
    """Individually valid collections cannot overflow a successor run."""
    fixture = core_fixture()
    artifacts = tuple(
        _artifact(index) for index in range(fixture.run.MAX_ARTIFACT_REFERENCES)
    )
    decisions = tuple(
        _decision(index, fixture.subject)
        for index in range(fixture.run.MAX_DECISION_REFERENCES)
    )
    start = WorkflowRunStarter().execute(
        definition=fixture.definition,
        subject_identity=fixture.subject,
        run_key=fixture.run.run_key,
        initial_state_references=fixture.state.state_references,
        artifact_references=artifacts,
        decision_references=decisions,
    )
    bounded_fixture = replace(fixture, run=start.run, state=start.state)
    transition = transition_input(bounded_fixture)
    extra_artifact = _artifact(len(artifacts))
    extra_decision = _decision(len(decisions), fixture.subject)
    evidence = WorkflowAdapterEvidence.create(
        adapter_identity=WorkflowAdapterIdentity("baseline:overflow"),
        definition_identity=fixture.definition.identity,
        request_identity=transition.request.identity,
        prior_state_identity=start.state.identity,
        disposition=WorkflowAdapterDisposition.ENABLED,
        successor_state_references=start.state.state_references,
        successor_run_status=WorkflowRunStatus.ACTIVE,
        produced_artifact_references=(extra_artifact,),
        recorded_decision_references=(extra_decision,),
    )

    execution = WorkflowTransitionProcessor().execute(
        replace(transition, adapter_evidence=evidence)
    )

    assert (
        execution.outcome.kind is WorkflowTransitionOutcomeKind.REJECTED_INVALID
    )
    assert execution.outcome.successor_run is None
    assert {
        finding.path for finding in execution.outcome.validation.findings
    } >= {
        ("successor_run", "artifact_references"),
        ("successor_run", "decision_references"),
    }


def test__transition_processor__caps_validation_findings() -> None:
    """Maximum invalid inputs produce a closed truncated validation result."""
    fixture = core_fixture()
    other_subject = WorkflowSubjectIdentity("source:other")
    request_decisions = tuple(
        sorted(
            (_decision(index, other_subject) for index in range(1024)),
            key=lambda item: item.identity.value,
        )
    )
    assert len(request_decisions) == 1024
    adapter_decisions = tuple(
        _decision(index, other_subject) for index in range(2000, 3024)
    )
    request = WorkflowTransitionRequest.create(
        run_identity=fixture.run.identity,
        expected_prior_state_identity=fixture.state.identity,
        expected_revision=fixture.run.revision,
        operation_identity=fixture.operation,
        input_references=(),
        artifact_references=(),
        decision_references=request_decisions,
        actor_identity=WorkflowActorIdentity("operator:test"),
        authority_reference=fixture.authority,
        idempotency_identity=WorkflowIdempotencyIdentity(
            "request:many-invalid"
        ),
        bounds=WorkflowRequestBounds(max_decision_references=1024),
    )
    evidence = WorkflowAdapterEvidence.create(
        adapter_identity=WorkflowAdapterIdentity("baseline:many-invalid"),
        definition_identity=fixture.definition.identity,
        request_identity=request.identity,
        prior_state_identity=fixture.state.identity,
        disposition=WorkflowAdapterDisposition.ENABLED,
        successor_state_references=fixture.state.state_references,
        successor_run_status=WorkflowRunStatus.ACTIVE,
        recorded_decision_references=adapter_decisions,
    )

    execution = WorkflowTransitionProcessor().execute(
        WorkflowTransitionInput(
            fixture.definition,
            fixture.run,
            fixture.state,
            request,
            evidence,
        )
    )

    findings = execution.outcome.validation.findings
    assert (
        execution.outcome.kind is WorkflowTransitionOutcomeKind.REJECTED_INVALID
    )
    assert len(findings) == execution.outcome.validation.MAX_FINDINGS
    assert findings[-1].code is WorkflowValidationFindingCode.FINDINGS_TRUNCATED
    assert len(execution.outcome.reasons) == execution.outcome.MAX_REASONS


def test__transition_execution__rejects_inconsistent_audit_event() -> None:
    """An unrelated audit event cannot pair with an outcome."""
    fixture = core_fixture()
    transition = transition_input(fixture)
    execution = WorkflowTransitionProcessor().execute(transition)
    event = execution.audit_event
    outcome = execution.outcome
    altered_events = (
        WorkflowAuditEvent.create(
            run_identity=WorkflowRunIdentity("run:other"),
            sequence_revision=event.sequence_revision,
            attempt_identity=event.attempt_identity,
            event_kind=event.event_kind,
            subject_references=event.subject_references,
            evidence_references=event.evidence_references,
        ),
        WorkflowAuditEvent.create(
            run_identity=event.run_identity,
            sequence_revision=event.sequence_revision + 1,
            attempt_identity=event.attempt_identity,
            event_kind=event.event_kind,
            subject_references=event.subject_references,
            evidence_references=event.evidence_references,
        ),
        WorkflowAuditEvent.create(
            run_identity=event.run_identity,
            sequence_revision=event.sequence_revision,
            attempt_identity=event.attempt_identity,
            event_kind="transition.blocked",
            subject_references=event.subject_references,
            evidence_references=event.evidence_references,
        ),
        WorkflowAuditEvent.create(
            run_identity=event.run_identity,
            sequence_revision=event.sequence_revision,
            attempt_identity=event.attempt_identity,
            event_kind=event.event_kind,
            subject_references=tuple(reversed(event.subject_references)),
            evidence_references=event.evidence_references,
        ),
        WorkflowAuditEvent.create(
            run_identity=event.run_identity,
            sequence_revision=event.sequence_revision,
            attempt_identity=event.attempt_identity,
            event_kind=event.event_kind,
            subject_references=event.subject_references,
            evidence_references=(
                WorkflowAuditReference(outcome.validation.identity),
            ),
        ),
    )

    for altered in altered_events:
        with pytest.raises(ValueError, match="inconsistent with its outcome"):
            WorkflowTransitionExecution(outcome, altered)


def test__transition_audit__uses_request_as_stable_attempt_order() -> None:
    """Same-revision nonapplications retain distinct deterministic attempts."""
    fixture = core_fixture()
    first_input = transition_input(
        fixture,
        disposition=WorkflowAdapterDisposition.BLOCKED,
    )
    first = WorkflowTransitionProcessor().execute(first_input)
    second_request = WorkflowTransitionRequest.create(
        run_identity=fixture.run.identity,
        expected_prior_state_identity=fixture.state.identity,
        expected_revision=fixture.run.revision,
        operation_identity=fixture.operation,
        input_references=(),
        artifact_references=(),
        decision_references=(),
        actor_identity=WorkflowActorIdentity("operator:test"),
        authority_reference=fixture.authority,
        idempotency_identity=WorkflowIdempotencyIdentity("request:second"),
    )
    second_evidence = WorkflowAdapterEvidence.create(
        adapter_identity=WorkflowAdapterIdentity("baseline:test"),
        definition_identity=fixture.definition.identity,
        request_identity=second_request.identity,
        prior_state_identity=fixture.state.identity,
        disposition=WorkflowAdapterDisposition.BLOCKED,
        reasons=("synthetic block",),
    )
    second = WorkflowTransitionProcessor().execute(
        WorkflowTransitionInput(
            fixture.definition,
            fixture.run,
            fixture.state,
            second_request,
            second_evidence,
        )
    )

    assert (
        first.audit_event.sequence_revision
        == second.audit_event.sequence_revision
    )
    assert first.audit_event.attempt_identity == first_input.request.identity
    assert second.audit_event.attempt_identity == second_request.identity
    assert (
        first.audit_event.attempt_identity
        != second.audit_event.attempt_identity
    )


def _artifact(index: int) -> WorkflowArtifactReference:
    return WorkflowArtifactReference.create(
        artifact_identity=WorkflowExternalReferenceIdentity(
            f"artifact:{index}"
        ),
        artifact_kind="synthetic",
        digest_sha256=f"{index:064x}",
        role="input",
        disposition=WorkflowArtifactDisposition.OBSERVED,
        provenance_identity=WorkflowExternalReferenceIdentity(
            f"provenance:{index}"
        ),
    )


def _decision(
    index: int,
    subject: WorkflowSubjectIdentity,
) -> WorkflowDecisionReference:
    return WorkflowDecisionReference.create(
        decision_kind="synthetic",
        scope="test",
        subject_identity=subject,
        authority_identity=WorkflowExternalReferenceIdentity(
            f"decision-authority:{index}"
        ),
        outcome="recorded",
        evidence_identity=WorkflowExternalReferenceIdentity(
            f"decision-evidence:{index}"
        ),
        decision_version="1",
    )
