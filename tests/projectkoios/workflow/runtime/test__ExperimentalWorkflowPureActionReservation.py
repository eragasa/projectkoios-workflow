"""Verification of bounded experimental predecessor reservation."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from _pure_action_fixtures import (
    _admitted,
    _authorized,
    _bindings,
    _coordinates,
    _evidence,
    _FixtureSourceRepository,
    _input_bindings,
    _predecessor,
    _service,
    _source,
)
from projectkoios.workflow.runtime import (
    ExperimentalInMemoryPureActionReservationRepository,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalWorkflowPureActionReserveStatus,
    ExperimentalWorkflowPureActionRevalidationStatus,
)


def test_reservation_revalidates_authorized_source_against_repository() -> None:
    claimed_source = _source(payload=b'{"claimed":true}')
    retained_source = _source(payload=b'{"retained":true}')
    service, _ = _service(retained_source)

    result = service.reserve(
        authorized_inputs=_authorized(_admitted(source=claimed_source))
    )

    assert result.status is (
        ExperimentalWorkflowPureActionReserveStatus.SOURCE_CONFLICT
    )
    assert result.reservation is None
    assert result.request is None


def test_source_identity_changes_reservation_even_when_request_is_exact() -> (
    None
):
    first_source = _source(source_identity="fixture.source-a")
    changed_source = _source(source_identity="fixture.source-b")
    first_service, _ = _service(first_source)
    changed_service, _ = _service(changed_source)
    first_admitted = _admitted(source=first_source)
    changed_admitted = _admitted(source=changed_source)

    first = first_service.reserve(authorized_inputs=_authorized(first_admitted))
    changed = changed_service.reserve(
        authorized_inputs=_authorized(changed_admitted)
    )

    assert first.request == changed.request
    assert first.reservation is not None
    assert changed.reservation is not None
    assert first.reservation.identity != changed.reservation.identity
    assert first.reservation.input_admission_identity == first_admitted.identity
    assert (
        changed.reservation.input_admission_identity
        == changed_admitted.identity
    )


def test_earlier_v0_reservation_shapes_remain_reconstructable() -> None:
    admitted = _admitted()
    service, _ = _service()
    result = service.reserve(authorized_inputs=_authorized(admitted))
    assert result.reservation is not None
    current = result.reservation

    legacy = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=current.execution_plan_identity,
        execution_bindings_identity=current.execution_bindings_identity,
        selected_binding_evidence_identity=(
            current.selected_binding_evidence_identity
        ),
        request_identity=current.request_identity,
        net_instance_identity=current.net_instance_identity,
        predecessor_marking_identity=current.predecessor_marking_identity,
        predecessor_revision=current.predecessor_revision,
        occurrence_identity=current.occurrence_identity,
        attempt_identity=current.attempt_identity,
        attempt_ordinal=current.attempt_ordinal,
    )

    admission_bound_shape = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=current.execution_plan_identity,
        execution_bindings_identity=current.execution_bindings_identity,
        selected_binding_evidence_identity=(
            current.selected_binding_evidence_identity
        ),
        request_identity=current.request_identity,
        net_instance_identity=current.net_instance_identity,
        predecessor_marking_identity=current.predecessor_marking_identity,
        predecessor_revision=current.predecessor_revision,
        occurrence_identity=current.occurrence_identity,
        attempt_identity=current.attempt_identity,
        attempt_ordinal=current.attempt_ordinal,
        input_admission_identity=current.input_admission_identity,
    )

    assert legacy.input_admission_identity is None
    assert legacy.input_authorization_identity is None
    assert legacy.identity.value == (
        "2189a0d705aa0523585e434eaa6efc922bcdda1c7535e217c671776a23e9baf7"
    )
    assert admission_bound_shape.input_authorization_identity is None
    assert admission_bound_shape.identity.value == (
        "b25d1dbecb22b1f593c04d3713568ba3dc716b241a1b98121900323fd0d541e2"
    )
    assert legacy.identity != admission_bound_shape.identity
    assert admission_bound_shape.identity != current.identity
    legacy_repository = ExperimentalInMemoryPureActionReservationRepository(
        (_predecessor(),)
    )
    assert legacy_repository.reserve(legacy) is (
        ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    assert legacy_repository.revalidate(legacy) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    )


def test_reserve_closes_plan_selection_request_and_current_predecessor() -> (
    None
):
    service, _ = _service()
    bindings = _bindings()
    evidence = _evidence()

    admitted = _admitted(
        input_bindings=_input_bindings(bindings=bindings),
        evidence=evidence,
    )
    authorized = _authorized(admitted)
    first = service.reserve(authorized_inputs=authorized)
    replay = service.reserve(authorized_inputs=authorized)

    assert first.status is ExperimentalWorkflowPureActionReserveStatus.RESERVED
    assert (
        replay.status is ExperimentalWorkflowPureActionReserveStatus.IDEMPOTENT
    )
    assert first.reservation == replay.reservation
    assert first.request == replay.request
    assert first.reservation is not None
    assert first.request is not None
    assert (
        first.reservation.execution_plan_identity
        == bindings.execution_plan.identity
    )
    assert first.reservation.execution_bindings_identity == bindings.identity
    assert (
        first.reservation.selected_binding_evidence_identity
        == evidence.identity
    )
    assert first.reservation.request_identity == first.request.identity
    assert first.reservation.input_admission_identity == admitted.identity
    assert first.reservation.input_authorization_identity == authorized.identity
    assert service.revalidate(first.reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    )


def test_stale_predecessor_fails_closed_before_owner_request_is_exposed() -> (
    None
):
    service, repository = _service()
    repository.advance_current_predecessor(
        _predecessor(marking="fixture.successor", revision=8)
    )

    result = service.reserve(authorized_inputs=_authorized())

    assert result.status is ExperimentalWorkflowPureActionReserveStatus.STALE
    assert result.reservation is None
    assert result.request is None


def test_post_owner_revalidation_detects_state_change_and_consumption() -> None:
    service, repository = _service()
    result = service.reserve(authorized_inputs=_authorized())
    assert result.reservation is not None

    repository.advance_current_predecessor(
        _predecessor(marking="fixture.successor", revision=8)
    )
    assert service.revalidate(result.reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.STALE
    )

    consumed_repository = ExperimentalInMemoryPureActionReservationRepository(
        (_predecessor(),),
        consumed_reservation_identities=(result.reservation.identity,),
    )
    consumed_service = ExperimentalWorkflowPureActionReservationService(
        consumed_repository,
        _FixtureSourceRepository((_source(),)),
    )
    assert consumed_service.revalidate(result.reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CONSUMED
    )


def test_in_memory_predecessor_cannot_rewind_and_resurrect_reservation() -> (
    None
):
    service, repository = _service()
    result = service.reserve(authorized_inputs=_authorized())
    assert result.reservation is not None
    repository.advance_current_predecessor(
        _predecessor(marking="fixture.successor", revision=8)
    )

    with pytest.raises(ValueError, match="revision must advance"):
        repository.advance_current_predecessor(_predecessor())
    assert service.revalidate(result.reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.STALE
    )


def test_concurrent_different_attempts_cannot_reserve_same_predecessor() -> (
    None
):
    service, _ = _service()
    barrier = Barrier(2)

    def reserve(attempt: str) -> ExperimentalWorkflowPureActionReserveStatus:
        barrier.wait()
        return service.reserve(
            authorized_inputs=_authorized(
                _admitted(coordinates=_coordinates(attempt=attempt))
            )
        ).status

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = tuple(
            executor.submit(reserve, attempt)
            for attempt in ("fixture.attempt-a", "fixture.attempt-b")
        )
        statuses = {future.result() for future in futures}

    assert statuses == {
        ExperimentalWorkflowPureActionReserveStatus.RESERVED,
        ExperimentalWorkflowPureActionReserveStatus.CONFLICT,
    }


def test_reservation_identity_changes_with_exact_request_inputs() -> None:
    first_source = _source(payload=b"{}")
    changed_source = _source(payload=b'{"changed":true}')
    first_service, _ = _service(first_source)
    changed_service, _ = _service(changed_source)
    bindings = _bindings()
    evidence = _evidence()

    input_bindings = _input_bindings(bindings=bindings)
    first = first_service.reserve(
        authorized_inputs=_authorized(
            _admitted(
                input_bindings=input_bindings,
                evidence=evidence,
                source=first_source,
            )
        )
    )
    changed = changed_service.reserve(
        authorized_inputs=_authorized(
            _admitted(
                input_bindings=input_bindings,
                evidence=evidence,
                source=changed_source,
            )
        )
    )

    assert first.reservation is not None
    assert changed.reservation is not None
    assert first.reservation.identity != changed.reservation.identity
    assert (
        first.reservation.request_identity
        != changed.reservation.request_identity
    )


def test_repository_rejects_forged_reservation_identity() -> None:
    service, _ = _service()
    result = service.reserve(authorized_inputs=_authorized())
    assert result.reservation is not None

    object.__setattr__(
        result.reservation,
        "identity",
        ExperimentalWorkflowPureActionReservationIdentity("0" * 64),
    )
    with pytest.raises(ValueError, match="differs after validation"):
        service.revalidate(result.reservation)


def test_admission_rejects_plan_selected_profile_substitution() -> None:
    bindings = _bindings(profile="fixture.retained-profile:1")

    with pytest.raises(ValueError, match="profile differs"):
        _admitted(input_bindings=_input_bindings(bindings=bindings))
