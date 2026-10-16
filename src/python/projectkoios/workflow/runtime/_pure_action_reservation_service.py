"""Service orchestration for experimental pure-action reservations."""

from __future__ import annotations

from typing import final

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlan,
    experimental_shadow_cpn_execution_profile,
)
from projectkoios.workflow_sdk.identities import WorkflowNetInstanceIdentity

from ._pure_action_reservation_port import (
    ExperimentalWorkflowPureActionReservationRepository,
)
from ._pure_action_reservation_records import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitReadResult,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReservationResult,
    ExperimentalWorkflowPureActionReserveStatus,
    ExperimentalWorkflowPureActionRevalidationStatus,
)
from .pure_action_input_authority import (
    ExperimentalWorkflowPureActionAuthorizedInputs,
)
from .pure_action_source_repository import (
    ExperimentalWorkflowPureActionInputSourceLoadResult,
    ExperimentalWorkflowPureActionInputSourceLoadStatus,
    ExperimentalWorkflowPureActionInputSourceReference,
    ExperimentalWorkflowPureActionInputSourceRepository,
)


@final
class ExperimentalWorkflowPureActionReservationService:
    """Construct an exact SDK request and reserve its current predecessor."""

    __slots__ = ("_repository", "_source_repository")

    def __init__(
        self,
        repository: ExperimentalWorkflowPureActionReservationRepository,
        source_repository: ExperimentalWorkflowPureActionInputSourceRepository,
    ) -> None:
        if not isinstance(
            repository,
            ExperimentalWorkflowPureActionReservationRepository,
        ):
            raise TypeError(
                "repository must implement "
                "ExperimentalWorkflowPureActionReservationRepository"
            )
        if not isinstance(
            source_repository,
            ExperimentalWorkflowPureActionInputSourceRepository,
        ):
            raise TypeError(
                "source_repository must implement "
                "ExperimentalWorkflowPureActionInputSourceRepository"
            )
        self._repository = repository
        self._source_repository = source_repository

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionReservationService "
            "is not subclassable"
        )

    def owns_repository(self, repository: object) -> bool:
        """Return whether this service owns the exact repository instance."""
        return repository is self._repository

    def reserve(
        self,
        *,
        authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs,
        cpn_plan: ExperimentalWorkflowPureActionCpnPlan | None = None,
    ) -> ExperimentalWorkflowPureActionReservationResult:
        """Reserve only a repository-authorized, plan-selected SDK request."""
        authorized = _reconstruct_authorized_inputs(authorized_inputs)
        admitted = authorized.admitted_inputs
        if cpn_plan is not None:
            if type(cpn_plan) is not ExperimentalWorkflowPureActionCpnPlan:
                raise TypeError(
                    "cpn_plan must be "
                    "ExperimentalWorkflowPureActionCpnPlan or None"
                )
            if (
                cpn_plan.input_plan_identity
                != admitted.input_bindings.input_plan.identity
            ):
                raise ValueError("CPN plan differs from admitted input plan")
            if (
                cpn_plan.execution_profile
                != experimental_shadow_cpn_execution_profile()
            ):
                raise ValueError("CPN execution profile is unsupported")
        source_status = self.revalidate_sources(authorized)
        if source_status is not None:
            return ExperimentalWorkflowPureActionReservationResult(
                status=source_status,
                reservation=None,
                request=None,
            )
        bindings = admitted.input_bindings.execution_bindings
        selected_binding_evidence = admitted.selected_binding_evidence
        request = admitted.request
        context = request.context
        reservation = ExperimentalWorkflowPureActionReservation(
            execution_plan_identity=bindings.execution_plan.identity,
            execution_bindings_identity=bindings.identity,
            selected_binding_evidence_identity=selected_binding_evidence.identity,
            request_identity=request.identity,
            net_instance_identity=context.net_instance_identity,
            predecessor_marking_identity=context.predecessor_marking_identity,
            predecessor_revision=context.predecessor_revision,
            occurrence_identity=context.occurrence_identity,
            attempt_identity=context.attempt_identity,
            attempt_ordinal=context.attempt_ordinal,
            input_admission_identity=admitted.identity,
            input_authorization_identity=authorized.identity,
            cpn_plan_identity=None if cpn_plan is None else cpn_plan.identity,
        )
        status = self._repository.reserve(reservation)
        if status in {
            ExperimentalWorkflowPureActionReserveStatus.RESERVED,
            ExperimentalWorkflowPureActionReserveStatus.IDEMPOTENT,
        }:
            return ExperimentalWorkflowPureActionReservationResult(
                status=status,
                reservation=reservation,
                request=request,
            )
        return ExperimentalWorkflowPureActionReservationResult(
            status=status,
            reservation=None,
            request=None,
        )

    def revalidate(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionRevalidationStatus:
        """Revalidate one exact reservation after owner execution."""
        return self._repository.revalidate(reservation)

    def commit(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord | None = None,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        """Atomically consume and advance through the repository boundary."""
        return self._repository.commit(reservation, coordinates, record)

    def load_committed_snapshot(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitReadResult:
        """Atomically load one closed compact committed snapshot result."""
        return self._repository.load_committed_snapshot(reservation_identity)

    def load_commit(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitCoordinates | None:
        """Load compact retained commit coordinates."""
        return self._repository.load_commit(reservation_identity)

    def load_commit_record(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitRecord | None:
        """Load the complete compact retained commit record."""
        return self._repository.load_commit_record(reservation_identity)

    def load_commit_event(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> bytes | None:
        """Load exact canonical retained commit-event bytes."""
        return self._repository.load_commit_event(reservation_identity)

    def current_predecessor(
        self,
        net_instance_identity: WorkflowNetInstanceIdentity,
    ) -> ExperimentalWorkflowPureActionCurrentPredecessor | None:
        """Load the repository-owned current predecessor coordinate."""
        return self._repository.current_predecessor(net_instance_identity)

    def revalidate_sources(
        self,
        authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs,
    ) -> ExperimentalWorkflowPureActionReserveStatus | None:
        """Re-resolve sources without reserving the predecessor."""
        authorized = _reconstruct_authorized_inputs(authorized_inputs)
        admitted = authorized.admitted_inputs
        for source, authority in zip(
            admitted.source_evidence,
            authorized.source_authorities,
            strict=True,
        ):
            reference = ExperimentalWorkflowPureActionInputSourceReference(
                source_kind=source.source_kind,
                source_profile_identity=source.source_profile_identity,
                source_identity=source.source_identity,
            )
            try:
                loaded = self._source_repository.load(reference)
            except Exception:
                return ExperimentalWorkflowPureActionReserveStatus.SOURCE_ERROR
            if type(loaded) is not (
                ExperimentalWorkflowPureActionInputSourceLoadResult
            ):
                return ExperimentalWorkflowPureActionReserveStatus.SOURCE_ERROR
            if loaded.status is not (
                ExperimentalWorkflowPureActionInputSourceLoadStatus.LOADED
            ):
                return _source_reserve_failure(loaded.status)
            if (
                loaded.evidence != source
                or loaded.revision_identity != authority.revision_identity
                or loaded.reference.identity != authority.reference_identity
            ):
                return (
                    ExperimentalWorkflowPureActionReserveStatus.SOURCE_CONFLICT
                )
        return None


def _source_reserve_failure(
    status: ExperimentalWorkflowPureActionInputSourceLoadStatus,
) -> ExperimentalWorkflowPureActionReserveStatus:
    return {
        ExperimentalWorkflowPureActionInputSourceLoadStatus.ABSENT: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_ABSENT
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.INCOMPATIBLE: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_INCOMPATIBLE
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.CORRUPT: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_CORRUPT
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.INDETERMINATE: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_INDETERMINATE
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.ERROR: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_ERROR
        ),
    }[status]


def _reconstruct_authorized_inputs(
    value: ExperimentalWorkflowPureActionAuthorizedInputs,
) -> ExperimentalWorkflowPureActionAuthorizedInputs:
    if type(value) is not ExperimentalWorkflowPureActionAuthorizedInputs:
        raise TypeError(
            "authorized_inputs must be "
            "ExperimentalWorkflowPureActionAuthorizedInputs"
        )
    reconstructed = ExperimentalWorkflowPureActionAuthorizedInputs(
        admitted_inputs=value.admitted_inputs,
        source_authorities=value.source_authorities,
    )
    if reconstructed != value:
        raise ValueError("authorized inputs differ after validation")
    return reconstructed


__all__ = ["ExperimentalWorkflowPureActionReservationService"]
