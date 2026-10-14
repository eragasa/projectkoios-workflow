"""Complete flat CPN definition validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ...definitions import (
    CpnArcDefinition,
    CpnDefinition,
)
from ...expressions.grammar import CpnTokenPattern
from ..findings import (
    CpnValidationIssue,
    CpnValidationIssueCode,
    CpnValidationResult,
)


@dataclass(frozen=True, slots=True)
class CpnInputArcValidationRequest:
    """Complete owner definition and exact input arc to validate."""

    definition: CpnDefinition
    arc: CpnArcDefinition

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.arc) is not CpnArcDefinition:
            raise TypeError("arc must be CpnArcDefinition")


@dataclass(frozen=True, slots=True)
class CpnInputArcValidationResponse:
    """Named response from one input-arc validation operation."""

    result: CpnValidationResult

    def __post_init__(self) -> None:
        if type(self.result) is not CpnValidationResult:
            raise TypeError("result must be CpnValidationResult")


@dataclass(frozen=True, slots=True)
class CpnInputArcValidatorIdentity:
    """Identity of exact input-arc validation semantics."""

    value: str = "projectkoios.workflow.cpn.input-arc-validator:0.1"


@final
class CpnInputArcValidator:
    """Validate one input arc without mutating a caller-owned issue list."""

    __slots__ = ()

    @property
    def identity(self) -> CpnInputArcValidatorIdentity:
        """Return exact input-arc validation semantics identity."""
        return CpnInputArcValidatorIdentity()

    def execute(
        self, request: CpnInputArcValidationRequest
    ) -> CpnInputArcValidationResponse:
        """Return named structural findings for one input arc."""
        if type(request) is not CpnInputArcValidationRequest:
            raise TypeError("request must be CpnInputArcValidationRequest")
        definition = request.definition
        arc = request.arc
        places = {item.identity: item for item in definition.places}
        transitions = {item.identity: item for item in definition.transitions}
        colors = {item.identity: item for item in definition.colors}
        place = places.get(arc.place_identity)
        transition = transitions.get(arc.transition_identity)
        if arc.input_inscription is None or transition is None:
            return CpnInputArcValidationResponse(CpnValidationResult(()))
        issues: list[CpnValidationIssue] = []
        declared = set(transition.input_variable_identities)
        for index, pattern in enumerate(arc.input_inscription.patterns):
            path = ("arcs", arc.identity.value, "input_patterns", str(index))
            for color_identity in pattern.allowed_color_identities:
                if color_identity not in colors:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.UNKNOWN_COLOR,
                            path + ("colors",),
                            (arc.identity.value, color_identity.value),
                            "input pattern references an unknown color",
                        )
                    )
                elif (
                    place is not None
                    and color_identity not in place.allowed_color_identities
                ):
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.COLOR_NOT_ALLOWED,
                            path + ("colors",),
                            (place.identity.value, color_identity.value),
                            "input pattern color is not admitted by the place",
                        )
                    )
            if (
                type(pattern) is CpnTokenPattern
                and pattern.variable_identity not in declared
            ):
                issues.append(
                    CpnValidationIssue(
                        CpnValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
                        path + ("variable",),
                        (
                            arc.transition_identity.value,
                            pattern.variable_identity.value,
                        ),
                        "input pattern binds an undeclared variable",
                    )
                )
        return CpnInputArcValidationResponse(CpnValidationResult(tuple(issues)))
