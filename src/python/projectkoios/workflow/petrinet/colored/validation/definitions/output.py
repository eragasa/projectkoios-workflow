"""Complete flat CPN definition validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ...definitions import (
    CpnArcDefinition,
    CpnDefinition,
)
from ...expressions.collection.expressions import (
    CpnExpressionVariableCollectionInput,
    CpnExpressionVariableCollector,
)
from ...expressions.errors import CpnExpressionOperationError
from ..findings import (
    CpnValidationIssue,
    CpnValidationIssueCode,
    CpnValidationResult,
)


@dataclass(frozen=True, slots=True)
class CpnOutputArcValidationRequest:
    """Complete owner definition and exact output arc to validate."""

    definition: CpnDefinition
    arc: CpnArcDefinition

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.arc) is not CpnArcDefinition:
            raise TypeError("arc must be CpnArcDefinition")


@dataclass(frozen=True, slots=True)
class CpnOutputArcValidationResponse:
    """Named response from one output-arc validation operation."""

    result: CpnValidationResult

    def __post_init__(self) -> None:
        if type(self.result) is not CpnValidationResult:
            raise TypeError("result must be CpnValidationResult")


@dataclass(frozen=True, slots=True)
class CpnOutputArcValidatorIdentity:
    """Identity of exact output-arc validation semantics."""

    value: str = "projectkoios.workflow.cpn.output-arc-validator:0.1"


@final
class CpnOutputArcValidator:
    """Validate one output arc without mutating caller-owned state."""

    __slots__ = ()

    @property
    def identity(self) -> CpnOutputArcValidatorIdentity:
        """Return exact output-arc validation semantics identity."""
        return CpnOutputArcValidatorIdentity()

    def execute(
        self, request: CpnOutputArcValidationRequest
    ) -> CpnOutputArcValidationResponse:
        """Return named structural findings for one output arc."""
        if type(request) is not CpnOutputArcValidationRequest:
            raise TypeError("request must be CpnOutputArcValidationRequest")
        definition = request.definition
        arc = request.arc
        places = {item.identity: item for item in definition.places}
        transitions = {item.identity: item for item in definition.transitions}
        colors = {item.identity: item for item in definition.colors}
        place = places.get(arc.place_identity)
        transition = transitions.get(arc.transition_identity)
        if arc.output_inscription is None or transition is None:
            return CpnOutputArcValidationResponse(CpnValidationResult(()))
        issues: list[CpnValidationIssue] = []
        declared = set(transition.input_variable_identities) | set(
            transition.external_output_variable_identities
        )
        for index, template in enumerate(arc.output_inscription.templates):
            path = ("arcs", arc.identity.value, "output_templates", str(index))
            if template.color_identity not in colors:
                issues.append(
                    CpnValidationIssue(
                        CpnValidationIssueCode.UNKNOWN_COLOR,
                        path + ("color",),
                        (arc.identity.value, template.color_identity.value),
                        "output template references an unknown color",
                    )
                )
            elif (
                place is not None
                and template.color_identity
                not in place.allowed_color_identities
            ):
                issues.append(
                    CpnValidationIssue(
                        CpnValidationIssueCode.COLOR_NOT_ALLOWED,
                        path + ("color",),
                        (place.identity.value, template.color_identity.value),
                        "output template color is not admitted by the place",
                    )
                )
            expressions = (template.value_expression,) + (
                ()
                if template.token_identity_expression is None
                else (template.token_identity_expression,)
            )
            for expression in expressions:
                try:
                    variables = (
                        CpnExpressionVariableCollector()
                        .execute(
                            CpnExpressionVariableCollectionInput(expression)
                        )
                        .variable_identities
                    )
                except CpnExpressionOperationError as exc:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.INVALID_VALUE_EXPRESSION,
                            path + ("expression",),
                            (arc.transition_identity.value, exc.code.value),
                            exc.diagnostic,
                        )
                    )
                    continue
                for variable in variables:
                    if variable not in declared:
                        issues.append(
                            CpnValidationIssue(
                                CpnValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
                                path + ("variable",),
                                (arc.transition_identity.value, variable.value),
                                "output template references an undeclared variable",
                            )
                        )
        return CpnOutputArcValidationResponse(
            CpnValidationResult(tuple(issues))
        )
