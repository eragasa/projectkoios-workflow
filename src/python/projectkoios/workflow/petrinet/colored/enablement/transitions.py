"""Complete deterministic transition enablement orchestration."""

from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import final
from ..definitions import CpnDefinition
from ..expressions.evaluation.expressions import CpnExpressionEvaluatorIdentity
from ..expressions.evaluation.guards import (
    CpnGuardEvaluationInput,
    CpnGuardEvaluator,
)
from ..expressions.grammar import CpnInputMode, CpnTokenPattern
from ..bindings import CpnBinding, CpnBindingAssignment
from ..markings import CpnMarking
from ..validation.definitions.complete import (
    CpnDefinitionValidationRequest,
    CpnDefinitionValidator,
)
from ..validation.markings import CpnMarkingValidationInput, CpnMarkingValidator
from ..values import CpnToken, CpnValue
from .failures.building import (
    CpnEnablementFailureBuilder,
    CpnEnablementFailureBuildingInput,
)
from .results.identity import (
    CpnEnablementFailureState,
    CpnEnablementResultIdentityDerivationInput,
    CpnEnablementResultIdentityDeriver,
)
from .ordering import (
    CpnEnabledBindingOrderingInput,
    CpnEnabledBindingOrderingPolicy,
)
from .results.definition import (
    CpnEnablementFailureCode,
    CpnEnablementResult,
    CpnOrderingPolicyIdentity,
    CpnTransitionEnablerIdentity,
)


_EXPRESSION_EVALUATOR_IDENTITY = CpnExpressionEvaluatorIdentity()


_ORDERING_POLICY_IDENTITY = CpnOrderingPolicyIdentity(
    "colored-petri-net-enablement-order-v1"
)


_TRANSITION_ENABLER_IDENTITY = CpnTransitionEnablerIdentity(
    "colored-petri-net-transition-enabler-v1"
)


@dataclass(frozen=True, slots=True)
class CpnTransitionEnablementRequest:
    """Complete immutable request for deterministic transition enablement."""

    definition: CpnDefinition
    marking: CpnMarking
    expression_evaluator_identity: CpnExpressionEvaluatorIdentity = (
        _EXPRESSION_EVALUATOR_IDENTITY
    )
    ordering_policy_identity: CpnOrderingPolicyIdentity = (
        _ORDERING_POLICY_IDENTITY
    )

    def __post_init__(self) -> None:
        expected = (
            ("definition", CpnDefinition),
            ("marking", CpnMarking),
            ("expression_evaluator_identity", CpnExpressionEvaluatorIdentity),
            ("ordering_policy_identity", CpnOrderingPolicyIdentity),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")


@final
class CpnTransitionEnabler:
    """ActionObject enumerating the complete enabled transition/binding set."""

    __slots__ = ()

    @property
    def identity(self) -> CpnTransitionEnablerIdentity:
        """Return exact complete-enablement semantics identity."""
        return _TRANSITION_ENABLER_IDENTITY

    def execute(
        self, request: CpnTransitionEnablementRequest
    ) -> CpnEnablementResult:
        """Return complete deterministic enablement or one structured failure.

        Wrong public argument types raise ``TypeError``. Cross-object defects,
        unsupported semantic versions, and guard failures are represented by the
        returned closed failure variant.
        """
        if type(request) is not CpnTransitionEnablementRequest:
            raise TypeError("request must be CpnTransitionEnablementRequest")
        definition = request.definition
        marking = request.marking
        expression_evaluator_identity = request.expression_evaluator_identity
        ordering_policy_identity = request.ordering_policy_identity
        common = (
            definition,
            marking,
            expression_evaluator_identity,
            ordering_policy_identity,
            _TRANSITION_ENABLER_IDENTITY,
        )
        failure_builder = CpnEnablementFailureBuilder()
        definition_validation = CpnDefinitionValidator().execute(
            CpnDefinitionValidationRequest(definition)
        )
        if not definition_validation.is_valid:
            return failure_builder.execute(
                CpnEnablementFailureBuildingInput(
                    *common,
                    CpnEnablementFailureState(
                        CpnEnablementFailureCode.INVALID_DEFINITION,
                        "definition_validation",
                        "a structurally valid colored Petri-net definition",
                        "definition validation returned findings",
                        "enablement was not evaluated",
                        definition_validation.issues,
                    ),
                )
            )
        marking_validation = CpnMarkingValidator().execute(
            CpnMarkingValidationInput(definition, marking)
        )
        if not marking_validation.is_valid:
            return failure_builder.execute(
                CpnEnablementFailureBuildingInput(
                    *common,
                    CpnEnablementFailureState(
                        CpnEnablementFailureCode.INVALID_MARKING,
                        "marking_validation",
                        "a complete marking compatible with the exact definition",
                        "marking validation returned findings",
                        "enablement was not evaluated",
                        marking_validation.issues,
                    ),
                )
            )
        if expression_evaluator_identity != _EXPRESSION_EVALUATOR_IDENTITY:
            return failure_builder.execute(
                CpnEnablementFailureBuildingInput(
                    *common,
                    CpnEnablementFailureState(
                        CpnEnablementFailureCode.UNSUPPORTED_EXPRESSION_EVALUATOR,
                        "expression_evaluator_resolution",
                        _EXPRESSION_EVALUATOR_IDENTITY.value,
                        expression_evaluator_identity.value,
                        "enablement was not evaluated under an unsupported semantic version",
                    ),
                )
            )
        if ordering_policy_identity != _ORDERING_POLICY_IDENTITY:
            return failure_builder.execute(
                CpnEnablementFailureBuildingInput(
                    *common,
                    CpnEnablementFailureState(
                        CpnEnablementFailureCode.UNSUPPORTED_ORDERING_POLICY,
                        "ordering_policy_resolution",
                        _ORDERING_POLICY_IDENTITY.value,
                        ordering_policy_identity.value,
                        "enablement was not evaluated under an unsupported semantic version",
                    ),
                )
            )

        enabled: set[CpnBinding] = set()
        by_place = {
            place.place_identity: place.tokens for place in marking.places
        }
        guard_evaluator = CpnGuardEvaluator()
        for transition in definition.transitions:
            arcs = tuple(
                arc
                for arc in definition.arcs
                if arc.transition_identity == transition.identity
                and arc.input_inscription is not None
            )
            inhibited = False
            demands: list[
                tuple[
                    object,
                    CpnInputMode,
                    CpnTokenPattern,
                ]
            ] = []
            candidates: list[tuple[tuple[int, CpnToken], ...]] = []
            for arc in arcs:
                inscription = arc.input_inscription
                assert inscription is not None
                tokens = by_place[arc.place_identity]
                if inscription.mode is CpnInputMode.INHIBIT:
                    for pattern in inscription.patterns:
                        if any(
                            token.color_identity
                            in pattern.allowed_color_identities
                            for token in tokens
                        ):
                            inhibited = True
                            break
                    if inhibited:
                        break
                    continue
                for pattern in inscription.patterns:
                    assert type(pattern) is CpnTokenPattern
                    demands.append(
                        (arc.place_identity, inscription.mode, pattern)
                    )
                    candidates.append(
                        tuple(
                            (index, token)
                            for index, token in enumerate(tokens)
                            if token.color_identity
                            in pattern.allowed_color_identities
                        )
                    )
            if inhibited or any(not items for items in candidates):
                continue
            choices = product(*candidates) if candidates else [()]
            for selected in choices:
                reserved: set[tuple[object, CpnInputMode, int]] = set()
                feasible = True
                values: dict[object, CpnValue] = {}
                for (place, mode, pattern), (index, token) in zip(
                    demands, selected, strict=True
                ):
                    key = (place, mode, index)
                    if key in reserved:
                        feasible = False
                        break
                    reserved.add(key)
                    values[pattern.variable_identity] = token.value
                if not feasible:
                    continue
                binding = CpnBinding(
                    transition.identity,
                    tuple(
                        CpnBindingAssignment(variable, values[variable])
                        for variable in transition.input_variable_identities
                    ),
                )
                try:
                    guard_value = guard_evaluator.execute(
                        CpnGuardEvaluationInput(
                            transition.guard,
                            binding,
                            definition.control_record_types,
                        )
                    ).value
                except (KeyError, TypeError, ValueError) as exc:
                    return failure_builder.execute(
                        CpnEnablementFailureBuildingInput(
                            *common,
                            CpnEnablementFailureState(
                                CpnEnablementFailureCode.GUARD_EVALUATION_FAILED,
                                "guard_evaluation",
                                "a total well-typed guard for every feasible binding",
                                f"guard failed for transition {transition.identity.value}",
                                f"{type(exc).__name__}: {exc}",
                            ),
                        )
                    )
                if guard_value:
                    enabled.add(binding)
        ordered = (
            CpnEnabledBindingOrderingPolicy()
            .execute(
                CpnEnabledBindingOrderingInput(definition, frozenset(enabled))
            )
            .bindings
        )
        identity = CpnEnablementResultIdentityDeriver().execute(
            CpnEnablementResultIdentityDerivationInput(*common, ordered, None)
        )
        return CpnEnablementResult(
            identity,
            definition.identity,
            definition.selection_policy,
            marking.identity,
            expression_evaluator_identity,
            ordering_policy_identity,
            _TRANSITION_ENABLER_IDENTITY,
            enabled_bindings=ordered,
        )
