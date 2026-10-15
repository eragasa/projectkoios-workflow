"""Experimental pure CPN firing after owner-result admission."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from string import hexdigits
from typing import final

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowCpnDefinitionEncoder,
    ExperimentalWorkflowPureActionCpnPlan,
    ExperimentalWorkflowPureActionCpnPlanIdentity,
    experimental_shadow_cpn_execution_profile,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetDefinition,
    ColoredPetriNetFiringInput,
    ColoredPetriNetFiringOutcomeKind,
    ColoredPetriNetFiringResult,
    ColoredPetriNetMarking,
    ColoredPetriNetTransitionFirer,
)
from projectkoios.workflow.runtime.pure_action_input_authority import (
    ExperimentalWorkflowPureActionAuthorizedInputs,
)
from projectkoios.workflow.runtime.pure_action_reservation import (
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationResult,
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalWorkflowPureActionRevalidationStatus,
)

from ._validation import (
    reconstruct_authorized_inputs,
    reconstruct_cpn_plan,
    reconstruct_successful_reservation,
)
from .pure_action_invocation import (
    ExperimentalWorkflowPureActionInvocationOutcome,
    ExperimentalWorkflowPureActionInvocationOutcomeIdentity,
    ExperimentalWorkflowPureActionInvocationStatus,
    _reconstruct_invocation_outcome,
)

_FIRING_OUTCOME_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-firing-outcome:0"
)
_MAX_DIAGNOSTICS = 16


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionFiringOutcomeIdentity:
    """Content identity of one bounded v0 pure-firing outcome."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "pure action firing outcome identity")


class ExperimentalWorkflowPureActionFiringStatus(StrEnum):
    """Closed v0 result of candidate pure CPN firing."""

    FIRED_CANDIDATE = "fired_candidate"
    CPN_REJECTED = "cpn_rejected"
    PRE_FIRE_STALE = "pre_fire_stale"
    POST_FIRE_STALE = "post_fire_stale"
    FIRING_ERROR = "firing_error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionFiringOutcome:
    """Retain a pure firing candidate without authorizing its commit."""

    identity: ExperimentalWorkflowPureActionFiringOutcomeIdentity = field(
        init=False
    )
    status: ExperimentalWorkflowPureActionFiringStatus
    invocation_outcome_identity: (
        ExperimentalWorkflowPureActionInvocationOutcomeIdentity
    )
    cpn_plan_identity: ExperimentalWorkflowPureActionCpnPlanIdentity
    firing_result: ColoredPetriNetFiringResult | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.status) is not ExperimentalWorkflowPureActionFiringStatus:
            raise TypeError(
                "status must be ExperimentalWorkflowPureActionFiringStatus"
            )
        if type(self.invocation_outcome_identity) is not (
            ExperimentalWorkflowPureActionInvocationOutcomeIdentity
        ):
            raise TypeError(
                "invocation_outcome_identity must be "
                "ExperimentalWorkflowPureActionInvocationOutcomeIdentity"
            )
        if type(self.cpn_plan_identity) is not (
            ExperimentalWorkflowPureActionCpnPlanIdentity
        ):
            raise TypeError(
                "cpn_plan_identity must be "
                "ExperimentalWorkflowPureActionCpnPlanIdentity"
            )
        _validate_diagnostics(self.diagnostics)
        result = self.firing_result
        if result is not None:
            if type(result) is not ColoredPetriNetFiringResult:
                raise TypeError(
                    "firing_result must be ColoredPetriNetFiringResult"
                )
            replayed = ColoredPetriNetTransitionFirer().execute(
                result.firing_input
            )
            if replayed != result:
                raise ValueError("firing result differs from pure replay")
        if self.status is (
            ExperimentalWorkflowPureActionFiringStatus.FIRED_CANDIDATE
        ):
            if (
                result is None
                or result.outcome
                is not ColoredPetriNetFiringOutcomeKind.SUCCESS
            ):
                raise ValueError("fired_candidate requires CPN success")
            if self.diagnostics:
                raise ValueError("fired_candidate prohibits diagnostics")
        elif self.status is (
            ExperimentalWorkflowPureActionFiringStatus.CPN_REJECTED
        ):
            if (
                result is None
                or result.outcome
                is not ColoredPetriNetFiringOutcomeKind.FAILURE
            ):
                raise ValueError("cpn_rejected requires CPN failure")
            if self.diagnostics:
                raise ValueError("cpn_rejected prohibits diagnostics")
        elif self.status is (
            ExperimentalWorkflowPureActionFiringStatus.POST_FIRE_STALE
        ):
            if result is None:
                raise ValueError("post_fire_stale requires a firing result")
            if not self.diagnostics:
                raise ValueError("post_fire_stale requires diagnostics")
        else:
            if result is not None:
                raise ValueError(f"{self.status.value} prohibits firing result")
            if not self.diagnostics:
                raise ValueError(f"{self.status.value} requires diagnostics")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionFiringOutcomeIdentity(
                stable_identity(
                    _FIRING_OUTCOME_DOMAIN,
                    self.status.value,
                    self.invocation_outcome_identity.value,
                    self.cpn_plan_identity.value,
                    None if result is None else result.identity.value,
                    self.diagnostics,
                )
            ),
        )


@final
class ExperimentalWorkflowPureActionFiringService:
    """Build and execute one exact pure CPN firing candidate."""

    __slots__ = ("_reservation_service",)

    def __init__(
        self,
        reservation_service: ExperimentalWorkflowPureActionReservationService,
    ) -> None:
        if type(reservation_service) is not (
            ExperimentalWorkflowPureActionReservationService
        ):
            raise TypeError(
                "reservation_service must be "
                "ExperimentalWorkflowPureActionReservationService"
            )
        self._reservation_service = reservation_service

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionFiringService is not subclassable"
        )

    def execute(
        self,
        *,
        authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs,
        reservation_result: ExperimentalWorkflowPureActionReservationResult,
        invocation_outcome: ExperimentalWorkflowPureActionInvocationOutcome,
        cpn_plan: ExperimentalWorkflowPureActionCpnPlan,
        definition: ColoredPetriNetDefinition,
        predecessor_marking: ColoredPetriNetMarking,
    ) -> ExperimentalWorkflowPureActionFiringOutcome:
        """Revalidate and compute a pure successor without committing it."""
        authorized = reconstruct_authorized_inputs(authorized_inputs)
        reservation, _ = reconstruct_successful_reservation(
            reservation_result,
            authorized,
            operation="pure firing",
        )
        invocation = _reconstruct_invocation_outcome(invocation_outcome)
        if invocation.status is not (
            ExperimentalWorkflowPureActionInvocationStatus.MAPPED
        ):
            raise ValueError("pure firing requires a mapped invocation outcome")
        plan = reconstruct_cpn_plan(cpn_plan)
        _validate_correlations(
            authorized=authorized,
            reservation=reservation,
            invocation=invocation,
            cpn_plan=plan,
            definition=definition,
            predecessor_marking=predecessor_marking,
        )
        stale = self._revalidation_diagnostics(authorized, reservation)
        if stale:
            return _outcome(
                status=ExperimentalWorkflowPureActionFiringStatus.PRE_FIRE_STALE,
                invocation=invocation,
                cpn_plan=plan,
                result=None,
                diagnostics=stale,
            )
        evidence = authorized.admitted_inputs.selected_binding_evidence
        selected_binding = evidence.selection_result.selected_binding
        mapped = invocation.mapped_result
        if selected_binding is None or mapped is None:
            raise ValueError("mapped invocation lacks exact CPN bindings")
        try:
            firing_input = ColoredPetriNetFiringInput(
                definition=definition,
                transition_identity=selected_binding.transition_identity,
                predecessor_marking=predecessor_marking,
                enablement_result=evidence.enablement_result,
                selection_result=evidence.selection_result,
                selected_binding=selected_binding,
                directive_identity=(
                    evidence.selection_result.directive_identity
                ),
                external_output_binding=mapped.external_output_binding,
            )
            result = ColoredPetriNetTransitionFirer().execute(firing_input)
        except Exception:
            return _outcome(
                status=ExperimentalWorkflowPureActionFiringStatus.FIRING_ERROR,
                invocation=invocation,
                cpn_plan=plan,
                result=None,
                diagnostics=("pure_cpn_firing_error",),
            )
        stale = self._revalidation_diagnostics(authorized, reservation)
        if stale:
            return _outcome(
                status=ExperimentalWorkflowPureActionFiringStatus.POST_FIRE_STALE,
                invocation=invocation,
                cpn_plan=plan,
                result=result,
                diagnostics=stale,
            )
        if result.outcome is ColoredPetriNetFiringOutcomeKind.FAILURE:
            return _outcome(
                status=ExperimentalWorkflowPureActionFiringStatus.CPN_REJECTED,
                invocation=invocation,
                cpn_plan=plan,
                result=result,
                diagnostics=(),
            )
        return _outcome(
            status=ExperimentalWorkflowPureActionFiringStatus.FIRED_CANDIDATE,
            invocation=invocation,
            cpn_plan=plan,
            result=result,
            diagnostics=(),
        )

    def _revalidation_diagnostics(
        self,
        authorized: ExperimentalWorkflowPureActionAuthorizedInputs,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> tuple[str, ...]:
        source_status = self._reservation_service.revalidate_sources(authorized)
        predecessor_status = self._reservation_service.revalidate(reservation)
        diagnostics = []
        if source_status is not None:
            diagnostics.append(source_status.value)
        if predecessor_status is not (
            ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
        ):
            diagnostics.append(f"reservation_{predecessor_status.value}")
        return tuple(diagnostics)


def _outcome(
    *,
    status: ExperimentalWorkflowPureActionFiringStatus,
    invocation: ExperimentalWorkflowPureActionInvocationOutcome,
    cpn_plan: ExperimentalWorkflowPureActionCpnPlan,
    result: ColoredPetriNetFiringResult | None,
    diagnostics: tuple[str, ...],
) -> ExperimentalWorkflowPureActionFiringOutcome:
    return ExperimentalWorkflowPureActionFiringOutcome(
        status=status,
        invocation_outcome_identity=invocation.identity,
        cpn_plan_identity=cpn_plan.identity,
        firing_result=result,
        diagnostics=diagnostics,
    )


def _validate_correlations(
    *,
    authorized: ExperimentalWorkflowPureActionAuthorizedInputs,
    reservation: ExperimentalWorkflowPureActionReservation,
    invocation: ExperimentalWorkflowPureActionInvocationOutcome,
    cpn_plan: ExperimentalWorkflowPureActionCpnPlan,
    definition: ColoredPetriNetDefinition,
    predecessor_marking: ColoredPetriNetMarking,
) -> None:
    if type(cpn_plan) is not ExperimentalWorkflowPureActionCpnPlan:
        raise TypeError(
            "cpn_plan must be ExperimentalWorkflowPureActionCpnPlan"
        )
    if type(definition) is not ColoredPetriNetDefinition:
        raise TypeError("definition must be ColoredPetriNetDefinition")
    if type(predecessor_marking) is not ColoredPetriNetMarking:
        raise TypeError("predecessor_marking must be ColoredPetriNetMarking")
    admitted = authorized.admitted_inputs
    evidence = admitted.selected_binding_evidence
    bindings = admitted.input_bindings.execution_bindings
    mapping = bindings.execution_plan.output_mapping_descriptor
    request = admitted.request
    context = request.context
    selected_binding = evidence.selection_result.selected_binding
    encoder = ExperimentalWorkflowCpnDefinitionEncoder()
    if (
        reservation.cpn_plan_identity != cpn_plan.identity
        or cpn_plan.input_plan_identity
        != admitted.input_bindings.input_plan.identity
        or cpn_plan.definition_identity != definition.identity
        or cpn_plan.definition_representation_profile_identity
        != encoder.profile_identity
        or cpn_plan.definition_bytes != encoder.encode(definition)
        or cpn_plan.execution_profile
        != experimental_shadow_cpn_execution_profile()
    ):
        raise ValueError("CPN plan differs from installed firing semantics")
    if selected_binding is None:
        raise ValueError("selected-binding evidence lacks a binding")
    if (
        invocation.reservation_identity != reservation.identity
        or invocation.input_authorization_identity != authorized.identity
        or invocation.request != request
        or invocation.mapped_result is None
        or invocation.mapped_result.mapping_descriptor != mapping
    ):
        raise ValueError("invocation differs from retained execution state")
    if (
        definition.identity != evidence.enablement_result.definition_identity
        or definition.identity.value != context.definition_identity.value
        or predecessor_marking.identity
        != evidence.enablement_result.marking_identity
        or predecessor_marking.identity.value
        != context.predecessor_marking_identity.value
        or predecessor_marking.definition_identity != definition.identity
        or selected_binding.transition_identity.value
        != context.transition_identity.value
        or selected_binding.transition_identity.value
        != mapping.transition_binding.transition_identity.value
        or reservation.predecessor_marking_identity
        != context.predecessor_marking_identity
        or reservation.predecessor_revision != context.predecessor_revision
    ):
        raise ValueError("CPN firing state differs from retained invocation")


def _reconstruct_firing_outcome(
    value: ExperimentalWorkflowPureActionFiringOutcome,
) -> ExperimentalWorkflowPureActionFiringOutcome:
    if type(value) is not ExperimentalWorkflowPureActionFiringOutcome:
        raise TypeError(
            "firing_outcome must be ExperimentalWorkflowPureActionFiringOutcome"
        )
    reconstructed = ExperimentalWorkflowPureActionFiringOutcome(
        status=value.status,
        invocation_outcome_identity=value.invocation_outcome_identity,
        cpn_plan_identity=value.cpn_plan_identity,
        firing_result=value.firing_result,
        diagnostics=value.diagnostics,
    )
    if reconstructed != value:
        raise ValueError("firing outcome differs after validation")
    return reconstructed


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


def _validate_diagnostics(values: tuple[str, ...]) -> None:
    if type(values) is not tuple:
        raise TypeError("diagnostics must be a tuple")
    if len(values) > _MAX_DIAGNOSTICS:
        raise ValueError("diagnostics exceed their bound")
    for value in values:
        if type(value) is not str or not value or len(value) > 128:
            raise ValueError(
                "diagnostics must contain bounded nonempty strings"
            )


__all__ = [
    "ExperimentalWorkflowPureActionFiringOutcome",
    "ExperimentalWorkflowPureActionFiringOutcomeIdentity",
    "ExperimentalWorkflowPureActionFiringService",
    "ExperimentalWorkflowPureActionFiringStatus",
]
