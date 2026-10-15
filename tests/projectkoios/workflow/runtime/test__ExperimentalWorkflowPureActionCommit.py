"""Verification of atomic pure-action commit."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest
from _pure_action_fixtures import (
    _commit_fixture,
    _invocation_fixture,
    _predecessor,
    _source,
)
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCommitService,
)
from projectkoios.workflow.persistence import (
    ExperimentalSQLitePureActionReservationRepository,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalWorkflowPureActionRevalidationStatus,
)
from projectkoios.workflow.runtime import (
    pure_action_reservation as reservation_module,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowMarkingIdentity,
)


def test_atomic_commit_consumes_reservation_and_advances_marking() -> None:
    candidate = _commit_fixture()
    fixture = candidate.invocation_fixture
    assert fixture.cpn_plan is not None
    service = ExperimentalWorkflowPureActionCommitService(
        fixture.reservation_service
    )

    committed = service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        cpn_plan=fixture.cpn_plan,
        invocation_outcome=candidate.invocation,
        firing_outcome=candidate.firing,
    )
    fixture.source_repository.replace(_source(payload=b'{"later":true}'))
    replayed = service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        cpn_plan=fixture.cpn_plan,
        invocation_outcome=candidate.invocation,
        firing_outcome=candidate.firing,
    )

    assert (
        committed.status is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    )
    assert committed.commit is not None
    assert committed.commit.identity.value == (
        "b58cbaf0c02fabf51c9d635bfbc8d6ecbcec6c1358e7e09580eb2544cf40e626"
    )
    assert (
        replayed.status is ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT
    )
    assert replayed.commit == committed.commit
    reservation = fixture.reservation_result.reservation
    assert reservation is not None
    assert fixture.reservation_service.revalidate(reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CONSUMED
    )
    retained = fixture.reservation_service.load_commit(reservation.identity)
    assert retained is not None
    assert retained.commit_identity == committed.commit.identity
    record = fixture.reservation_service.load_commit_record(
        reservation.identity
    )
    assert record is not None
    assert record.commit_identity == committed.commit.identity
    assert record.source_authorities == fixture.authorized.source_authorities
    assert (
        record.invocation_outcome_identity
        == candidate.invocation.identity.value
    )
    assert record.firing_outcome_identity == candidate.firing.identity.value
    current = fixture.reservation_service.current_predecessor(
        reservation.net_instance_identity
    )
    assert current is not None
    assert (
        current.marking_identity == committed.commit.successor_marking_identity
    )
    assert current.revision == committed.commit.successor_revision
    assert not hasattr(committed.commit, "request")
    assert not hasattr(committed.commit, "result")


def test_atomic_commit_service_persists_complete_record_durably(
    tmp_path: Path,
) -> None:
    candidate = _commit_fixture()
    fixture = candidate.invocation_fixture
    assert fixture.cpn_plan is not None
    durable_repository = ExperimentalSQLitePureActionReservationRepository(
        tmp_path / "private" / "pure-action.sqlite3",
        predecessors=(_predecessor(),),
    )
    reservation_service = ExperimentalWorkflowPureActionReservationService(
        durable_repository,
        fixture.source_repository,
    )
    reservation_result = reservation_service.reserve(
        authorized_inputs=fixture.authorized,
        cpn_plan=fixture.cpn_plan,
    )
    assert (
        reservation_result.reservation == fixture.reservation_result.reservation
    )

    committed = ExperimentalWorkflowPureActionCommitService(
        reservation_service
    ).execute(
        authorized_inputs=fixture.authorized,
        reservation_result=reservation_result,
        cpn_plan=fixture.cpn_plan,
        invocation_outcome=candidate.invocation,
        firing_outcome=candidate.firing,
    )

    assert (
        committed.status is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    )
    assert committed.commit is not None
    reopened = ExperimentalSQLitePureActionReservationRepository(
        durable_repository.database_path
    )
    retained = reopened.load_commit_record(
        reservation_result.reservation.identity
    )
    assert retained is not None
    assert retained.commit_identity == committed.commit.identity
    assert retained.source_authorities == fixture.authorized.source_authorities


def test_atomic_commit_allows_one_concurrent_winner() -> None:
    candidate = _commit_fixture()
    fixture = candidate.invocation_fixture
    assert fixture.cpn_plan is not None
    service = ExperimentalWorkflowPureActionCommitService(
        fixture.reservation_service
    )

    def commit() -> ExperimentalWorkflowPureActionCommitStatus:
        return service.execute(
            authorized_inputs=fixture.authorized,
            reservation_result=fixture.reservation_result,
            cpn_plan=fixture.cpn_plan,
            invocation_outcome=candidate.invocation,
            firing_outcome=candidate.firing,
        ).status

    with ThreadPoolExecutor(max_workers=8) as executor:
        statuses = tuple(executor.map(lambda _: commit(), range(8)))

    assert (
        statuses.count(ExperimentalWorkflowPureActionCommitStatus.COMMITTED)
        == 1
    )
    assert (
        statuses.count(ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT)
        == 7
    )


def test_atomic_commit_rejects_distinct_concurrent_commits() -> None:
    fixture = _invocation_fixture()
    reservation = fixture.reservation_result.reservation
    assert reservation is not None
    first = ExperimentalWorkflowPureActionCommitCoordinates(
        commit_identity=ExperimentalWorkflowPureActionCommitIdentity("1" * 64),
        reservation_identity=reservation.identity,
        net_instance_identity=reservation.net_instance_identity,
        predecessor_marking_identity=reservation.predecessor_marking_identity,
        predecessor_revision=reservation.predecessor_revision,
        successor_marking_identity=WorkflowMarkingIdentity(
            "fixture.successor.a"
        ),
        successor_revision=reservation.predecessor_revision + 1,
    )
    second = replace(
        first,
        commit_identity=ExperimentalWorkflowPureActionCommitIdentity("2" * 64),
        successor_marking_identity=WorkflowMarkingIdentity(
            "fixture.successor.b"
        ),
    )

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = tuple(
            executor.map(
                lambda coordinates: fixture.predecessor_repository.commit(
                    reservation,
                    coordinates,
                ),
                (first, second),
            )
        )

    assert (
        statuses.count(ExperimentalWorkflowPureActionCommitStatus.COMMITTED)
        == 1
    )
    assert (
        statuses.count(ExperimentalWorkflowPureActionCommitStatus.CONFLICT) == 1
    )


def test_atomic_commit_failure_before_swap_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _commit_fixture()
    fixture = candidate.invocation_fixture
    assert fixture.cpn_plan is not None
    reservation = fixture.reservation_result.reservation
    assert reservation is not None

    def fail_before_swap(*args: object) -> None:
        del args
        raise RuntimeError("injected pre-swap failure")

    monkeypatch.setattr(
        reservation_module,
        "_finalize_commit_state",
        fail_before_swap,
    )
    with pytest.raises(RuntimeError, match="injected pre-swap failure"):
        ExperimentalWorkflowPureActionCommitService(
            fixture.reservation_service
        ).execute(
            authorized_inputs=fixture.authorized,
            reservation_result=fixture.reservation_result,
            cpn_plan=fixture.cpn_plan,
            invocation_outcome=candidate.invocation,
            firing_outcome=candidate.firing,
        )

    assert fixture.reservation_service.revalidate(reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    )
    assert fixture.reservation_service.load_commit(reservation.identity) is None
    current = fixture.reservation_service.current_predecessor(
        reservation.net_instance_identity
    )
    assert current == _predecessor()


def test_atomic_commit_revalidates_sources_before_commit() -> None:
    candidate = _commit_fixture()
    fixture = candidate.invocation_fixture
    assert fixture.cpn_plan is not None
    fixture.source_repository.replace(_source(payload=b'{"changed":true}'))

    result = ExperimentalWorkflowPureActionCommitService(
        fixture.reservation_service
    ).execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        cpn_plan=fixture.cpn_plan,
        invocation_outcome=candidate.invocation,
        firing_outcome=candidate.firing,
    )

    assert result.status is ExperimentalWorkflowPureActionCommitStatus.STALE
    assert result.commit is None
    reservation = fixture.reservation_result.reservation
    assert reservation is not None
    assert fixture.reservation_service.revalidate(reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    )
