"""Shared fixtures for durable CPN replay evidence tests."""

from pathlib import Path

from _pure_action_fixtures import _commit_fixture
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCpnReplayBundleFactory,
    ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec,
    experimental_cpn_replay_evidence,
)
from projectkoios.workflow.execution.pure_action_commit import (
    _construct_commit,
    _construct_commit_record,
)
from projectkoios.workflow.persistence import (
    ExperimentalSQLitePureActionReservationRepository,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalWorkflowPureActionReserveStatus,
)


def _candidate(tmp_path: Path):  # type: ignore[no-untyped-def]
    fixture = _commit_fixture()
    invocation_fixture = fixture.invocation_fixture
    plan = invocation_fixture.cpn_plan
    assert plan is not None
    reservation = invocation_fixture.reservation_result.reservation
    assert reservation is not None
    firing_result = fixture.firing.firing_result
    assert firing_result is not None
    repository = ExperimentalSQLitePureActionReservationRepository(
        tmp_path / "private" / "pure-action.sqlite3",
        predecessors=(
            ExperimentalWorkflowPureActionCurrentPredecessor(
                net_instance_identity=reservation.net_instance_identity,
                marking_identity=reservation.predecessor_marking_identity,
                revision=reservation.predecessor_revision,
            ),
        ),
    )
    assert (
        repository.reserve(reservation)
        is ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    commit = _construct_commit(
        authorized=invocation_fixture.authorized,
        reservation=reservation,
        plan=plan,
        invocation=fixture.invocation,
        firing=fixture.firing,
    )
    record = _construct_commit_record(commit, invocation_fixture.authorized)
    coordinates = ExperimentalWorkflowPureActionCommitCoordinates(
        commit_identity=commit.identity,
        reservation_identity=commit.reservation_identity,
        net_instance_identity=reservation.net_instance_identity,
        predecessor_marking_identity=commit.predecessor_marking_identity,
        predecessor_revision=commit.predecessor_revision,
        successor_marking_identity=commit.successor_marking_identity,
        successor_revision=commit.successor_revision,
    )
    bundle = ExperimentalWorkflowPureActionCpnReplayBundleFactory().execute(
        cpn_plan=plan,
        firing_result=firing_result,
    )
    bundle_bytes = (
        ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().encode(bundle)
    )
    evidence = experimental_cpn_replay_evidence(record, bundle_bytes)
    return repository, reservation, coordinates, record, evidence


def _durable_orchestration(tmp_path: Path):  # type: ignore[no-untyped-def]
    fixture = _commit_fixture()
    invocation_fixture = fixture.invocation_fixture
    plan = invocation_fixture.cpn_plan
    assert plan is not None
    expected_reservation = invocation_fixture.reservation_result.reservation
    assert expected_reservation is not None
    repository = ExperimentalSQLitePureActionReservationRepository(
        tmp_path / "orchestrated" / "pure-action.sqlite3",
        predecessors=(
            ExperimentalWorkflowPureActionCurrentPredecessor(
                net_instance_identity=expected_reservation.net_instance_identity,
                marking_identity=expected_reservation.predecessor_marking_identity,
                revision=expected_reservation.predecessor_revision,
            ),
        ),
    )
    reservation_service = ExperimentalWorkflowPureActionReservationService(
        repository,
        invocation_fixture.source_repository,
    )
    reservation_result = reservation_service.reserve(
        authorized_inputs=invocation_fixture.authorized,
        cpn_plan=plan,
    )
    assert reservation_result.reservation == expected_reservation
    return fixture, plan, repository, reservation_service, reservation_result
