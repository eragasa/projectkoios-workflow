"""Verification of bounded pure-action owner invocation."""

import pytest
from _pure_action_fixtures import (
    _FixtureWorkerIntegration,
    _invocation_fixture,
    _predecessor,
    _transition,
)
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionInvocationStatus,
)
from projectkoios.workflow_sdk.firing import (
    WorkflowFiringFailed,
    WorkflowFiringRejected,
    WorkflowFiringSucceeded,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowIntegrationManifestIdentity,
)


def test_invocation_maps_only_current_correlated_owner_success() -> None:
    fixture = _invocation_fixture()

    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=_transition(),
    )

    assert (
        outcome.status is ExperimentalWorkflowPureActionInvocationStatus.MAPPED
    )
    assert outcome.identity.value == (
        "61e0065affc56078cf07d9470a0abbda9da8e550696b8b5e85f2ca611b608246"
    )
    assert type(outcome.result) is WorkflowFiringSucceeded
    assert outcome.mapped_result is not None
    assignment = outcome.mapped_result.external_output_binding.assignments[0]
    assert assignment.value.value == "fixture.owner.artifact-set:1"
    assert fixture.firer.calls == 1


@pytest.mark.parametrize(
    ("owner_outcome", "expected_status", "result_type"),
    (
        (
            "rejected",
            ExperimentalWorkflowPureActionInvocationStatus.OWNER_REJECTED,
            WorkflowFiringRejected,
        ),
        (
            "failed",
            ExperimentalWorkflowPureActionInvocationStatus.OWNER_FAILED,
            WorkflowFiringFailed,
        ),
    ),
)
def test_invocation_preserves_closed_owner_non_success(
    owner_outcome: str,
    expected_status: ExperimentalWorkflowPureActionInvocationStatus,
    result_type: type[WorkflowFiringRejected] | type[WorkflowFiringFailed],
) -> None:
    fixture = _invocation_fixture(outcome=owner_outcome)

    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=_transition(),
    )

    assert outcome.status is expected_status
    assert type(outcome.result) is result_type
    assert outcome.mapped_result is None


def test_invocation_rejects_stale_precondition_without_calling_owner() -> None:
    fixture = _invocation_fixture()
    fixture.predecessor_repository.advance_current_predecessor(
        _predecessor(marking="fixture.successor", revision=8)
    )

    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=_transition(),
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionInvocationStatus.PRE_INVOKE_STALE
    )
    assert outcome.result is None
    assert outcome.mapped_result is None
    assert fixture.firer.calls == 0


def test_invocation_preserves_result_but_does_not_map_after_state_change() -> (
    None
):
    fixture = _invocation_fixture(stale_during_fire=True)

    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=_transition(),
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionInvocationStatus.POST_INVOKE_STALE
    )
    assert type(outcome.result) is WorkflowFiringSucceeded
    assert outcome.mapped_result is None
    assert fixture.firer.calls == 1


def test_invocation_does_not_map_after_source_changes_during_owner_call() -> (
    None
):
    fixture = _invocation_fixture(change_source_during_fire=True)

    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=_transition(),
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionInvocationStatus.POST_INVOKE_STALE
    )
    assert type(outcome.result) is WorkflowFiringSucceeded
    assert outcome.mapped_result is None
    assert outcome.diagnostics == ("source_conflict",)


def test_invocation_revalidates_after_live_worker_resolution() -> None:
    fixture = _invocation_fixture()

    def make_stale() -> None:
        fixture.predecessor_repository.advance_current_predecessor(
            _predecessor(marking="fixture.successor", revision=8)
        )

    integration = _FixtureWorkerIntegration(
        fixture.integration.manifest_identity,
        (fixture.firer,),
        callback=make_stale,
    )
    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=integration,
        transition=_transition(),
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionInvocationStatus.PRE_INVOKE_STALE
    )
    assert outcome.diagnostics == ("reservation_stale",)
    assert fixture.firer.calls == 0


def test_invocation_rejects_worker_mismatch_before_owner_call() -> None:
    fixture = _invocation_fixture()
    mismatched = _FixtureWorkerIntegration(
        WorkflowIntegrationManifestIdentity("0" * 64),
        (fixture.firer,),
    )

    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=mismatched,
        transition=_transition(),
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionInvocationStatus.WORKER_REJECTED
    )
    assert outcome.result is None
    assert fixture.firer.calls == 0


def test_invocation_contains_attempted_owner_request_mutation() -> None:
    fixture = _invocation_fixture(outcome="mutate_request")

    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=_transition(),
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionInvocationStatus.INVOCATION_ERROR
    )
    assert outcome.request == fixture.authorized.admitted_inputs.request
    assert outcome.result is None
    assert outcome.mapped_result is None


def test_invocation_contains_owner_exception_and_revalidates_state() -> None:
    fixture = _invocation_fixture(
        outcome="error",
        stale_during_fire=True,
    )

    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=_transition(),
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionInvocationStatus.INVOCATION_ERROR
    )
    assert outcome.result is None
    assert outcome.mapped_result is None
    assert outcome.diagnostics == (
        "owner_invocation_error",
        "reservation_stale",
    )


def test_invocation_rejects_success_that_cannot_map_to_transition() -> None:
    fixture = _invocation_fixture()

    outcome = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=_transition("other_output"),
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionInvocationStatus.RESULT_REJECTED
    )
    assert type(outcome.result) is WorkflowFiringSucceeded
    assert outcome.mapped_result is None
