"""Verification of CPN plan closure and pure firing."""

from dataclasses import replace

import pytest
from _pure_action_fixtures import (
    _authorized,
    _cpn_firing_fixture,
    _cpn_plan,
    _input_bindings,
    _invocation_fixture,
    _predecessor,
    _service,
    _source,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowCpnDefinitionEncoder,
    ExperimentalWorkflowPureActionCpnPlanFactory,
    experimental_shadow_cpn_execution_profile,
)
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionFiringService,
    ExperimentalWorkflowPureActionFiringStatus,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetColorIdentity,
    ColoredPetriNetSelectionPolicy,
    ColoredPetriNetValueKind,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionRevalidationStatus,
)


def test_cpn_plan_closes_definition_bytes_and_execution_profile() -> None:
    definition, _, _ = _cpn_firing_fixture()
    input_plan = _input_bindings().input_plan
    profile = experimental_shadow_cpn_execution_profile()
    plan = ExperimentalWorkflowPureActionCpnPlanFactory().execute(
        input_plan=input_plan,
        definition=definition,
        execution_profile=profile,
    )
    changed_definition = replace(
        definition,
        selection_policy=ColoredPetriNetSelectionPolicy.DIRECTED_ALLOWED,
    )
    changed_definition_plan = (
        ExperimentalWorkflowPureActionCpnPlanFactory().execute(
            input_plan=input_plan,
            definition=changed_definition,
            execution_profile=profile,
        )
    )
    changed_profile_plan = (
        ExperimentalWorkflowPureActionCpnPlanFactory().execute(
            input_plan=input_plan,
            definition=definition,
            execution_profile=replace(
                profile,
                transition_firer_identity="shadow-cpn-transition-firer:other",
            ),
        )
    )

    assert (
        plan.definition_bytes
        == ExperimentalWorkflowCpnDefinitionEncoder().encode(definition)
    )
    assert plan.definition_sha256 == (
        "1344efeb8246cdef7d0bf720dd1ac06f08663ff9ca95bc93d88fe380a0d42234"
    )
    assert plan.identity.value == (
        "ccfe9ca78f04da9167ef8237d81ccf048d1f09cf6765b8b8210ca7774f16b982"
    )
    assert plan.definition_sha256 != changed_definition_plan.definition_sha256
    assert plan.identity != changed_definition_plan.identity
    assert plan.identity != changed_profile_plan.identity
    invalid_definition = replace(
        definition,
        places=(
            replace(
                definition.places[0],
                allowed_color_identities=(
                    ColoredPetriNetColorIdentity("unknown.color"),
                ),
            ),
        ),
    )
    with pytest.raises(ValueError, match="invalid CPN definition"):
        replace(
            plan,
            definition_bytes=ExperimentalWorkflowCpnDefinitionEncoder().encode(
                invalid_definition
            ),
        )
    authorized = _authorized()
    reservation_service, _ = _service(_source())
    with pytest.raises(ValueError, match="execution profile is unsupported"):
        reservation_service.reserve(
            authorized_inputs=authorized,
            cpn_plan=changed_profile_plan,
        )


def test_pure_firing_computes_candidate_successor_without_consuming() -> None:
    definition, marking, evidence = _cpn_firing_fixture()
    fixture = _invocation_fixture(
        evidence=evidence,
        cpn_definition=definition,
    )
    invocation = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=definition.transitions[0],
    )

    outcome = ExperimentalWorkflowPureActionFiringService(
        fixture.reservation_service
    ).execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        invocation_outcome=invocation,
        cpn_plan=_cpn_plan(fixture, definition),
        definition=definition,
        predecessor_marking=marking,
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionFiringStatus.FIRED_CANDIDATE
    )
    assert outcome.identity.value == (
        "83f48104089bcda48cbd5a2b80509da4a3897048b36009ed8340f0ff9ff9a59e"
    )
    assert outcome.firing_result is not None
    assert outcome.firing_result.successor_marking is not None
    successor = outcome.firing_result.successor_marking
    assert successor.places[0].tokens[0].value.value == (
        "fixture.owner.artifact-set:1"
    )
    reservation = fixture.reservation_result.reservation
    assert reservation is not None
    assert fixture.cpn_plan is not None
    assert reservation.cpn_plan_identity == fixture.cpn_plan.identity
    assert fixture.reservation_service.revalidate(reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    )


def test_pure_firing_rejects_definition_content_substitution() -> None:
    definition, marking, evidence = _cpn_firing_fixture()
    fixture = _invocation_fixture(
        evidence=evidence,
        cpn_definition=definition,
    )
    invocation = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=definition.transitions[0],
    )
    substituted_definition = replace(
        definition,
        selection_policy=ColoredPetriNetSelectionPolicy.DIRECTED_ALLOWED,
    )
    substituted_plan = ExperimentalWorkflowPureActionCpnPlanFactory().execute(
        input_plan=fixture.authorized.admitted_inputs.input_bindings.input_plan,
        definition=substituted_definition,
        execution_profile=experimental_shadow_cpn_execution_profile(),
    )

    with pytest.raises(ValueError, match="CPN plan differs"):
        ExperimentalWorkflowPureActionFiringService(
            fixture.reservation_service
        ).execute(
            authorized_inputs=fixture.authorized,
            reservation_result=fixture.reservation_result,
            invocation_outcome=invocation,
            cpn_plan=substituted_plan,
            definition=definition,
            predecessor_marking=marking,
        )


def test_pure_firing_preserves_cpn_output_color_rejection() -> None:
    definition, marking, evidence = _cpn_firing_fixture(
        color_kind=ColoredPetriNetValueKind.INTEGER
    )
    fixture = _invocation_fixture(
        evidence=evidence,
        cpn_definition=definition,
    )
    invocation = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=definition.transitions[0],
    )

    outcome = ExperimentalWorkflowPureActionFiringService(
        fixture.reservation_service
    ).execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        invocation_outcome=invocation,
        cpn_plan=_cpn_plan(fixture, definition),
        definition=definition,
        predecessor_marking=marking,
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionFiringStatus.CPN_REJECTED
    )
    assert outcome.firing_result is not None
    assert outcome.firing_result.failure is not None
    assert outcome.firing_result.successor_marking is None


def test_pure_firing_revalidates_before_computing_successor() -> None:
    definition, marking, evidence = _cpn_firing_fixture()
    fixture = _invocation_fixture(
        evidence=evidence,
        cpn_definition=definition,
    )
    invocation = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=definition.transitions[0],
    )
    fixture.predecessor_repository.advance_current_predecessor(
        _predecessor(marking="fixture.other", revision=8)
    )

    outcome = ExperimentalWorkflowPureActionFiringService(
        fixture.reservation_service
    ).execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        invocation_outcome=invocation,
        cpn_plan=_cpn_plan(fixture, definition),
        definition=definition,
        predecessor_marking=marking,
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionFiringStatus.PRE_FIRE_STALE
    )
    assert outcome.firing_result is None
    assert outcome.diagnostics == ("reservation_stale",)


def test_pure_firing_preserves_candidate_but_blocks_stale_commit() -> None:
    definition, marking, evidence = _cpn_firing_fixture()
    fixture = _invocation_fixture(
        evidence=evidence,
        cpn_definition=definition,
    )
    invocation = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=definition.transitions[0],
    )
    fixture.source_repository.replace_after_loads(
        1,
        _source(payload=b'{"changed":true}'),
    )

    outcome = ExperimentalWorkflowPureActionFiringService(
        fixture.reservation_service
    ).execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        invocation_outcome=invocation,
        cpn_plan=_cpn_plan(fixture, definition),
        definition=definition,
        predecessor_marking=marking,
    )

    assert outcome.status is (
        ExperimentalWorkflowPureActionFiringStatus.POST_FIRE_STALE
    )
    assert outcome.firing_result is not None
    assert outcome.firing_result.successor_marking is not None
    assert outcome.diagnostics == ("source_conflict",)
