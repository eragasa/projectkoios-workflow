"""Experimental owner invocation and result admission for pure actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from string import hexdigits
from typing import final

from projectkoios.workflow.actions import (
    ExperimentalWorkflowAsciiOutputMapper,
    ExperimentalWorkflowMappedActionResult,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetTransitionDefinition,
)
from projectkoios.workflow.runtime.pure_action_input_authority import (
    ExperimentalWorkflowPureActionAuthorizedInputs,
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
)
from projectkoios.workflow.runtime.pure_action_reservation import (
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReservationResult,
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalWorkflowPureActionReserveStatus,
    ExperimentalWorkflowPureActionRevalidationStatus,
)
from projectkoios.workflow.worker import WorkflowWorkerIntegrationValidator
from projectkoios.workflow_sdk.firing import (
    Firer,
    WorkflowFiringFailed,
    WorkflowFiringRejected,
    WorkflowFiringRequest,
    WorkflowFiringResult,
    WorkflowFiringSucceeded,
)
from projectkoios.workflow_sdk.integration import WorkflowWorkerIntegration
from projectkoios.workflow_sdk.serialization import (
    WorkflowFiringRequestJsonCodec,
    WorkflowFiringResultJsonCodec,
)

from ._validation import (
    reconstruct_authorized_inputs,
    reconstruct_successful_reservation,
)

_INVOCATION_OUTCOME_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-invocation-outcome:0"
)
_MAX_DIAGNOSTICS = 16


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInvocationOutcomeIdentity:
    """Content identity of one bounded v0 invocation outcome."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "pure action invocation outcome identity")


class ExperimentalWorkflowPureActionInvocationStatus(StrEnum):
    """Closed v0 result of owner invocation and result admission."""

    MAPPED = "mapped"
    OWNER_REJECTED = "owner_rejected"
    OWNER_FAILED = "owner_failed"
    PRE_INVOKE_STALE = "pre_invoke_stale"
    POST_INVOKE_STALE = "post_invoke_stale"
    WORKER_REJECTED = "worker_rejected"
    INVOCATION_ERROR = "invocation_error"
    RESULT_REJECTED = "result_rejected"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInvocationOutcome:
    """Retain one invocation result without granting CPN firing authority."""

    identity: ExperimentalWorkflowPureActionInvocationOutcomeIdentity = field(
        init=False
    )
    status: ExperimentalWorkflowPureActionInvocationStatus
    reservation_identity: ExperimentalWorkflowPureActionReservationIdentity
    input_authorization_identity: (
        ExperimentalWorkflowPureActionAuthorizedInputsIdentity
    )
    request: WorkflowFiringRequest
    result: WorkflowFiringResult | None
    mapped_result: ExperimentalWorkflowMappedActionResult | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.status)
            is not ExperimentalWorkflowPureActionInvocationStatus
        ):
            raise TypeError(
                "status must be ExperimentalWorkflowPureActionInvocationStatus"
            )
        if type(self.reservation_identity) is not (
            ExperimentalWorkflowPureActionReservationIdentity
        ):
            raise TypeError(
                "reservation_identity must be "
                "ExperimentalWorkflowPureActionReservationIdentity"
            )
        if type(self.input_authorization_identity) is not (
            ExperimentalWorkflowPureActionAuthorizedInputsIdentity
        ):
            raise TypeError(
                "input_authorization_identity must be "
                "ExperimentalWorkflowPureActionAuthorizedInputsIdentity"
            )
        request = _round_trip_request(self.request)
        result = (
            None if self.result is None else _round_trip_result(self.result)
        )
        mapped = (
            None
            if self.mapped_result is None
            else _reconstruct_mapped_result(self.mapped_result)
        )
        _validate_diagnostics(self.diagnostics)
        if (
            self.status
            in {
                ExperimentalWorkflowPureActionInvocationStatus.MAPPED,
                ExperimentalWorkflowPureActionInvocationStatus.OWNER_REJECTED,
                ExperimentalWorkflowPureActionInvocationStatus.OWNER_FAILED,
            }
            and self.diagnostics
        ):
            raise ValueError(f"{self.status.value} prohibits diagnostics")
        if (
            self.status
            not in {
                ExperimentalWorkflowPureActionInvocationStatus.MAPPED,
                ExperimentalWorkflowPureActionInvocationStatus.OWNER_REJECTED,
                ExperimentalWorkflowPureActionInvocationStatus.OWNER_FAILED,
            }
            and not self.diagnostics
        ):
            raise ValueError(f"{self.status.value} requires diagnostics")
        if result is not None and result.request_identity != request.identity:
            raise ValueError("invocation result differs from request")
        if self.status is ExperimentalWorkflowPureActionInvocationStatus.MAPPED:
            if type(result) is not WorkflowFiringSucceeded or mapped is None:
                raise ValueError("mapped status requires success and mapping")
            if (
                mapped.request_identity != request.identity
                or mapped.result_identity != result.identity
            ):
                raise ValueError("mapped result differs from invocation result")
        elif mapped is not None:
            raise ValueError("non-mapped status prohibits mapped result")
        if (
            self.status
            is (ExperimentalWorkflowPureActionInvocationStatus.OWNER_REJECTED)
            and type(result) is not WorkflowFiringRejected
        ):
            raise ValueError("owner_rejected requires rejected SDK result")
        if (
            self.status
            is (ExperimentalWorkflowPureActionInvocationStatus.OWNER_FAILED)
            and type(result) is not WorkflowFiringFailed
        ):
            raise ValueError("owner_failed requires failed SDK result")
        if (
            self.status
            is ExperimentalWorkflowPureActionInvocationStatus.RESULT_REJECTED
            and type(result) is not WorkflowFiringSucceeded
        ):
            raise ValueError("result_rejected requires successful SDK result")
        if (
            self.status
            in {
                ExperimentalWorkflowPureActionInvocationStatus.PRE_INVOKE_STALE,
                ExperimentalWorkflowPureActionInvocationStatus.WORKER_REJECTED,
                ExperimentalWorkflowPureActionInvocationStatus.INVOCATION_ERROR,
            }
            and result is not None
        ):
            raise ValueError(f"{self.status.value} prohibits SDK result")
        if (
            self.status
            is (
                ExperimentalWorkflowPureActionInvocationStatus.POST_INVOKE_STALE
            )
            and result is None
        ):
            raise ValueError("post_invoke_stale requires SDK result")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionInvocationOutcomeIdentity(
                stable_identity(
                    _INVOCATION_OUTCOME_DOMAIN,
                    self.status.value,
                    self.reservation_identity.value,
                    self.input_authorization_identity.value,
                    request.identity.value,
                    None if result is None else result.identity.value,
                    None if mapped is None else mapped.identity.value,
                    self.diagnostics,
                )
            ),
        )


@final
class ExperimentalWorkflowPureActionInvocationService:
    """Invoke one exact owner firer and admit only a current mapped success."""

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
            "ExperimentalWorkflowPureActionInvocationService "
            "is not subclassable"
        )

    def execute(
        self,
        *,
        authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs,
        reservation_result: ExperimentalWorkflowPureActionReservationResult,
        integration: WorkflowWorkerIntegration,
        transition: ColoredPetriNetTransitionDefinition,
    ) -> ExperimentalWorkflowPureActionInvocationOutcome:
        """Invoke, correlate, revalidate, and map without firing the CPN."""
        authorized = reconstruct_authorized_inputs(authorized_inputs)
        reservation, request = reconstruct_successful_reservation(
            reservation_result,
            authorized,
            operation="invocation",
        )
        source_status = self._reservation_service.revalidate_sources(authorized)
        predecessor_status = self._reservation_service.revalidate(reservation)
        if (
            source_status is not None
            or predecessor_status
            is not ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
        ):
            return _outcome(
                status=(
                    ExperimentalWorkflowPureActionInvocationStatus.PRE_INVOKE_STALE
                ),
                reservation=reservation,
                authorized=authorized,
                request=request,
                result=None,
                mapped=None,
                diagnostics=_stale_diagnostics(
                    source_status,
                    predecessor_status,
                ),
            )
        bindings = authorized.admitted_inputs.input_bindings.execution_bindings
        try:
            firers = WorkflowWorkerIntegrationValidator().execute(
                manifest=bindings.integration_manifest,
                integration=integration,
            )
            firer = _select_firer(firers, request)
        except Exception:
            return _outcome(
                status=(
                    ExperimentalWorkflowPureActionInvocationStatus.WORKER_REJECTED
                ),
                reservation=reservation,
                authorized=authorized,
                request=request,
                result=None,
                mapped=None,
                diagnostics=("worker_integration_rejected",),
            )
        source_status = self._reservation_service.revalidate_sources(authorized)
        predecessor_status = self._reservation_service.revalidate(reservation)
        if (
            source_status is not None
            or predecessor_status
            is not ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
        ):
            return _outcome(
                status=(
                    ExperimentalWorkflowPureActionInvocationStatus.PRE_INVOKE_STALE
                ),
                reservation=reservation,
                authorized=authorized,
                request=request,
                result=None,
                mapped=None,
                diagnostics=_stale_diagnostics(
                    source_status,
                    predecessor_status,
                ),
            )
        owner_request = _round_trip_request(request)
        try:
            result = _round_trip_result(firer.fire(request=owner_request))
            if _round_trip_request(owner_request) != request:
                raise ValueError("owner mutated its isolated request")
        except Exception:
            source_status = self._reservation_service.revalidate_sources(
                authorized
            )
            predecessor_status = self._reservation_service.revalidate(
                reservation
            )
            return _outcome(
                status=(
                    ExperimentalWorkflowPureActionInvocationStatus.INVOCATION_ERROR
                ),
                reservation=reservation,
                authorized=authorized,
                request=request,
                result=None,
                mapped=None,
                diagnostics=("owner_invocation_error",)
                + _stale_diagnostics(source_status, predecessor_status),
            )
        source_status = self._reservation_service.revalidate_sources(authorized)
        predecessor_status = self._reservation_service.revalidate(reservation)
        if (
            source_status is not None
            or predecessor_status
            is not ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
        ):
            return _outcome(
                status=(
                    ExperimentalWorkflowPureActionInvocationStatus.POST_INVOKE_STALE
                ),
                reservation=reservation,
                authorized=authorized,
                request=request,
                result=result,
                mapped=None,
                diagnostics=_stale_diagnostics(
                    source_status,
                    predecessor_status,
                ),
            )
        if type(result) is WorkflowFiringRejected:
            return _outcome(
                status=(
                    ExperimentalWorkflowPureActionInvocationStatus.OWNER_REJECTED
                ),
                reservation=reservation,
                authorized=authorized,
                request=request,
                result=result,
                mapped=None,
                diagnostics=(),
            )
        if type(result) is WorkflowFiringFailed:
            return _outcome(
                status=(
                    ExperimentalWorkflowPureActionInvocationStatus.OWNER_FAILED
                ),
                reservation=reservation,
                authorized=authorized,
                request=request,
                result=result,
                mapped=None,
                diagnostics=(),
            )
        if type(result) is not WorkflowFiringSucceeded:
            raise TypeError("closed SDK result is not a recognized variant")
        mapping = bindings.execution_plan.output_mapping_descriptor
        try:
            mapped = ExperimentalWorkflowAsciiOutputMapper().execute(
                mapping=mapping,
                transition=transition,
                expected_context=request.context,
                request=request,
                result=result,
            )
        except TypeError, ValueError:
            return _outcome(
                status=(
                    ExperimentalWorkflowPureActionInvocationStatus.RESULT_REJECTED
                ),
                reservation=reservation,
                authorized=authorized,
                request=request,
                result=result,
                mapped=None,
                diagnostics=("result_mapping_rejected",),
            )
        return _outcome(
            status=ExperimentalWorkflowPureActionInvocationStatus.MAPPED,
            reservation=reservation,
            authorized=authorized,
            request=request,
            result=result,
            mapped=mapped,
            diagnostics=(),
        )


def _outcome(
    *,
    status: ExperimentalWorkflowPureActionInvocationStatus,
    reservation: ExperimentalWorkflowPureActionReservation,
    authorized: ExperimentalWorkflowPureActionAuthorizedInputs,
    request: WorkflowFiringRequest,
    result: WorkflowFiringResult | None,
    mapped: ExperimentalWorkflowMappedActionResult | None,
    diagnostics: tuple[str, ...],
) -> ExperimentalWorkflowPureActionInvocationOutcome:
    return ExperimentalWorkflowPureActionInvocationOutcome(
        status=status,
        reservation_identity=reservation.identity,
        input_authorization_identity=authorized.identity,
        request=request,
        result=result,
        mapped_result=mapped,
        diagnostics=diagnostics,
    )


def _select_firer(
    firers: tuple[Firer, ...],
    request: WorkflowFiringRequest,
) -> Firer:
    matches = tuple(
        firer
        for firer in firers
        if firer.descriptor.identity == request.firer_identity
    )
    if len(matches) != 1:
        raise ValueError("worker integration does not resolve one exact firer")
    return matches[0]


def _stale_diagnostics(
    source_status: ExperimentalWorkflowPureActionReserveStatus | None,
    predecessor_status: ExperimentalWorkflowPureActionRevalidationStatus,
) -> tuple[str, ...]:
    diagnostics = []
    if source_status is not None:
        diagnostics.append(source_status.value)
    if predecessor_status is not (
        ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    ):
        diagnostics.append(f"reservation_{predecessor_status.value}")
    return tuple(diagnostics)


def _reconstruct_invocation_outcome(
    value: ExperimentalWorkflowPureActionInvocationOutcome,
) -> ExperimentalWorkflowPureActionInvocationOutcome:
    if type(value) is not ExperimentalWorkflowPureActionInvocationOutcome:
        raise TypeError(
            "invocation_outcome must be "
            "ExperimentalWorkflowPureActionInvocationOutcome"
        )
    reconstructed = ExperimentalWorkflowPureActionInvocationOutcome(
        status=value.status,
        reservation_identity=value.reservation_identity,
        input_authorization_identity=value.input_authorization_identity,
        request=value.request,
        result=value.result,
        mapped_result=value.mapped_result,
        diagnostics=value.diagnostics,
    )
    if reconstructed != value:
        raise ValueError("invocation outcome differs after validation")
    return reconstructed


def _round_trip_request(value: WorkflowFiringRequest) -> WorkflowFiringRequest:
    if type(value) is not WorkflowFiringRequest:
        raise TypeError("request must be WorkflowFiringRequest")
    codec = WorkflowFiringRequestJsonCodec()
    reconstructed = codec.decode(codec.encode(value))
    if reconstructed != value:
        raise ValueError("request differs after canonical round trip")
    return reconstructed


def _round_trip_result(value: WorkflowFiringResult) -> WorkflowFiringResult:
    if type(value) not in {
        WorkflowFiringSucceeded,
        WorkflowFiringRejected,
        WorkflowFiringFailed,
    }:
        raise TypeError("result must be a closed SDK firing result")
    codec = WorkflowFiringResultJsonCodec()
    reconstructed = codec.decode(codec.encode(value))
    if reconstructed != value:
        raise ValueError("result differs after canonical round trip")
    return reconstructed


def _reconstruct_mapped_result(
    value: ExperimentalWorkflowMappedActionResult,
) -> ExperimentalWorkflowMappedActionResult:
    if type(value) is not ExperimentalWorkflowMappedActionResult:
        raise TypeError(
            "mapped_result must be ExperimentalWorkflowMappedActionResult"
        )
    reconstructed = ExperimentalWorkflowMappedActionResult(
        mapping_descriptor=value.mapping_descriptor,
        request_identity=value.request_identity,
        result_identity=value.result_identity,
        external_output_binding=ColoredPetriNetBinding(
            transition_identity=value.external_output_binding.transition_identity,
            assignments=value.external_output_binding.assignments,
        ),
        source_output=value.source_output,
        evidence=value.evidence,
    )
    if reconstructed != value:
        raise ValueError("mapped result differs after validation")
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
    "ExperimentalWorkflowPureActionInvocationOutcome",
    "ExperimentalWorkflowPureActionInvocationOutcomeIdentity",
    "ExperimentalWorkflowPureActionInvocationService",
    "ExperimentalWorkflowPureActionInvocationStatus",
]
