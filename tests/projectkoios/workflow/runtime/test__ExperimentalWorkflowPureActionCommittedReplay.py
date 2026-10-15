"""Verification of read-only compact pure-action committed replay."""

from _pure_action_fixtures import _commit_fixture, _predecessor
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCommitService,
    ExperimentalWorkflowPureActionCommittedReplayService,
    ExperimentalWorkflowPureActionCommittedReplayStatus,
)
from projectkoios.workflow.runtime import (
    ExperimentalInMemoryPureActionReservationRepository,
    ExperimentalWorkflowPureActionReservationIdentity,
)


def test_committed_replay_reconstructs_without_reinvoking_owner() -> None:
    candidate = _commit_fixture()
    fixture = candidate.invocation_fixture
    assert fixture.cpn_plan is not None
    committed = ExperimentalWorkflowPureActionCommitService(
        fixture.reservation_service
    ).execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        cpn_plan=fixture.cpn_plan,
        invocation_outcome=candidate.invocation,
        firing_outcome=candidate.firing,
    )
    reservation = fixture.reservation_result.reservation
    assert reservation is not None
    owner_calls = fixture.firer.calls

    replayed = ExperimentalWorkflowPureActionCommittedReplayService(
        fixture.predecessor_repository
    ).execute(reservation.identity)

    assert (
        replayed.status
        is ExperimentalWorkflowPureActionCommittedReplayStatus.REPLAYED
    )
    assert replayed.commit == committed.commit
    assert replayed.coordinates is not None
    assert (
        replayed.coordinates.net_instance_identity
        == reservation.net_instance_identity
    )
    assert replayed.event_sha256 is not None
    assert len(replayed.event_sha256) == 64
    assert replayed.diagnostics == ()
    assert fixture.firer.calls == owner_calls


def test_committed_replay_reports_absent_without_owner_or_source_access() -> (
    None
):
    repository = ExperimentalInMemoryPureActionReservationRepository(
        (_predecessor(),)
    )
    replayed = ExperimentalWorkflowPureActionCommittedReplayService(
        repository
    ).execute(ExperimentalWorkflowPureActionReservationIdentity("0" * 64))

    assert (
        replayed.status
        is ExperimentalWorkflowPureActionCommittedReplayStatus.ABSENT
    )
    assert replayed.commit is None
    assert replayed.coordinates is None
    assert replayed.event_sha256 is None
    assert replayed.diagnostics == ("commit_absent",)
