"""Identity-bound enablement failure construction."""

from __future__ import annotations
from dataclasses import dataclass
from typing import final
from ..definitions import CpnDefinition
from ..expressions.evaluation import CpnExpressionEvaluatorIdentity
from ..markings import CpnMarking
from .identity_derivation import (
    CpnEnablementFailureState,
    CpnEnablementResultIdentityDerivationInput,
    CpnEnablementResultIdentityDeriver,
)
from .outcomes import (
    CpnEnablementFailure,
    CpnEnablementFailureIdentity,
    CpnEnablementResult,
    CpnOrderingPolicyIdentity,
    CpnTransitionEnablerIdentity,
)


@dataclass(frozen=True, slots=True)
class CpnEnablementFailureBuildingInput:
    """Complete immutable input for one enablement failure response."""

    definition: CpnDefinition
    marking: CpnMarking
    expression_identity: CpnExpressionEvaluatorIdentity
    ordering_identity: CpnOrderingPolicyIdentity
    enabler_identity: CpnTransitionEnablerIdentity
    failure_state: CpnEnablementFailureState

    def __post_init__(self) -> None:
        expected = (
            ("definition", CpnDefinition),
            ("marking", CpnMarking),
            ("expression_identity", CpnExpressionEvaluatorIdentity),
            ("ordering_identity", CpnOrderingPolicyIdentity),
            ("enabler_identity", CpnTransitionEnablerIdentity),
            ("failure_state", CpnEnablementFailureState),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")


@dataclass(frozen=True, slots=True)
class CpnEnablementFailureBuilderIdentity:
    """Identity of exact enablement-failure construction semantics."""

    value: str = "projectkoios.workflow.cpn.enablement-failure-builder:0.1"


@final
class CpnEnablementFailureBuilder:
    """Construct one identity-bound enablement failure response."""

    __slots__ = ()

    @property
    def identity(self) -> CpnEnablementFailureBuilderIdentity:
        """Return exact failure-construction semantics identity."""
        return CpnEnablementFailureBuilderIdentity()

    def execute(
        self, building_input: CpnEnablementFailureBuildingInput
    ) -> CpnEnablementResult:
        """Return one complete failure result from typed immutable input."""
        if type(building_input) is not CpnEnablementFailureBuildingInput:
            raise TypeError(
                "building_input must be CpnEnablementFailureBuildingInput"
            )
        state = building_input.failure_state
        result_identity = CpnEnablementResultIdentityDeriver().execute(
            CpnEnablementResultIdentityDerivationInput(
                building_input.definition,
                building_input.marking,
                building_input.expression_identity,
                building_input.ordering_identity,
                building_input.enabler_identity,
                None,
                state,
            )
        )
        failure = CpnEnablementFailure(
            CpnEnablementFailureIdentity(result_identity),
            state.code,
            state.operation_phase,
            state.expected_condition,
            state.observed_condition,
            state.diagnostic,
            state.validation_issues,
        )
        return CpnEnablementResult(
            result_identity,
            building_input.definition.identity,
            building_input.definition.selection_policy,
            building_input.marking.identity,
            building_input.expression_identity,
            building_input.ordering_identity,
            building_input.enabler_identity,
            failure=failure,
        )
