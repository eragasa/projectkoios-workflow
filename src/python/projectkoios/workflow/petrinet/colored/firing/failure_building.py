"""Identity-bound pure-firing failure construction."""

from __future__ import annotations
from dataclasses import dataclass
from typing import final
from .identity_derivation import (
    CpnFiringFailureState,
    CpnFiringResultIdentityDerivationRequest,
    CpnFiringResultIdentityDeriver,
)
from .inputs import CpnFiringInput
from .results import (
    CpnFiringFailure,
    CpnFiringFailureIdentity,
    CpnFiringOutcomeKind,
    CpnFiringResult,
)


@dataclass(frozen=True, slots=True)
class CpnFiringFailureBuildingRequest:
    """One firing input and structured failure state."""

    firing_input: CpnFiringInput
    failure: CpnFiringFailureState


@dataclass(frozen=True, slots=True)
class CpnFiringFailureBuilderIdentity:
    """Identity of exact firing-failure construction semantics."""

    value: str = "projectkoios.workflow.cpn.firing-failure-builder:0.1"


@final
class CpnFiringFailureBuilder:
    """Construct one complete identity-bound firing failure response."""

    __slots__ = ()

    @property
    def identity(self) -> CpnFiringFailureBuilderIdentity:
        """Return exact failure-building semantics identity."""
        return CpnFiringFailureBuilderIdentity()

    def execute(
        self, request: CpnFiringFailureBuildingRequest
    ) -> CpnFiringResult:
        """Return one complete firing failure."""
        if type(request) is not CpnFiringFailureBuildingRequest:
            raise TypeError("request must be CpnFiringFailureBuildingRequest")
        state = request.failure
        identity = CpnFiringResultIdentityDeriver().execute(
            CpnFiringResultIdentityDerivationRequest(
                request.firing_input, failure=state
            )
        )
        failure = CpnFiringFailure(
            CpnFiringFailureIdentity(identity),
            state.code,
            state.phase,
            state.expected,
            state.observed,
            "firing produced no successor",
            state.issues,
        )
        return CpnFiringResult(
            identity,
            request.firing_input,
            CpnFiringOutcomeKind.FAILURE,
            failure=failure,
        )
