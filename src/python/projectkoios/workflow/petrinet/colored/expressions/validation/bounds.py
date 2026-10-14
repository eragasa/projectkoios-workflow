"""Closed CPN expression validation operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ...values import (
    CpnControlRecordTypeDefinition,
)
from ..grammar import (
    CpnGuardExpression,
    CpnValueExpression,
)
from ..collection.guards import (
    CpnGuardExpressionCollectionInput,
    CpnGuardExpressionCollector,
)
from .structure import (
    CpnExpressionStructureValidationInput,
    CpnExpressionStructureValidator,
)
from ..errors import (
    CpnExpressionOperationError,
    CpnExpressionOperationErrorCode,
)


@dataclass(frozen=True, slots=True)
class CpnExpressionBoundsValidatorIdentity:
    """Identity of exact per-transition expression-bound semantics."""

    value: str = "projectkoios.workflow.cpn.expression-bounds-validator:0.1"


@dataclass(frozen=True, slots=True)
class CpnExpressionBoundsValidationInput:
    """One guard, output expressions, and exact retained record schemas."""

    guard: CpnGuardExpression
    output_expressions: tuple[CpnValueExpression, ...]
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...]

    def __post_init__(self) -> None:
        if type(self.guard) is not CpnGuardExpression:
            raise TypeError("guard must be CpnGuardExpression")
        if type(self.output_expressions) is not tuple or any(
            type(item) is not CpnValueExpression
            for item in self.output_expressions
        ):
            raise TypeError(
                "output_expressions must be a tuple of CpnValueExpression"
            )
        if type(self.type_definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.type_definitions
        ):
            raise TypeError(
                "type_definitions must be a tuple of "
                "CpnControlRecordTypeDefinition"
            )


@dataclass(frozen=True, slots=True)
class CpnExpressionBoundsValidationResult:
    """Exact aggregate dimensions and ordered expression findings."""

    total_node_count: int
    maximum_depth: int
    issues: tuple[CpnExpressionOperationError, ...]

    def __post_init__(self) -> None:
        for name in ("total_node_count", "maximum_depth"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise TypeError(f"{name} must be a nonnegative integer")
        if type(self.issues) is not tuple or any(
            type(item) is not CpnExpressionOperationError
            for item in self.issues
        ):
            raise TypeError("issues must be CpnExpressionOperationError tuple")

    @property
    def is_valid(self) -> bool:
        """Return whether every aggregate and per-expression bound holds."""
        return not self.issues


@final
class CpnExpressionBoundsValidator:
    """Directly validate guard/output depth and aggregate transition nodes."""

    __slots__ = ()

    @property
    def identity(self) -> CpnExpressionBoundsValidatorIdentity:
        """Return exact bound-validation semantics identity."""
        return CpnExpressionBoundsValidatorIdentity()

    def execute(
        self, validation_input: CpnExpressionBoundsValidationInput
    ) -> CpnExpressionBoundsValidationResult:
        """Validate every expression and the total 4096-node transition bound."""
        if type(validation_input) is not CpnExpressionBoundsValidationInput:
            raise TypeError(
                "validation_input must be CpnExpressionBoundsValidationInput"
            )
        issues: list[CpnExpressionOperationError] = []
        total_nodes = 0
        maximum_depth = 0
        try:
            guard_result = CpnGuardExpressionCollector().execute(
                CpnGuardExpressionCollectionInput(validation_input.guard)
            )
            total_nodes += guard_result.guard_node_count
            maximum_depth = max(maximum_depth, guard_result.maximum_guard_depth)
            expressions = (
                guard_result.expressions + validation_input.output_expressions
            )
        except CpnExpressionOperationError as exc:
            issues.append(exc)
            expressions = validation_input.output_expressions
        for index, expression in enumerate(expressions):
            result = CpnExpressionStructureValidator().execute(
                CpnExpressionStructureValidationInput(
                    expression, validation_input.type_definitions
                )
            )
            total_nodes += result.node_count
            maximum_depth = max(maximum_depth, result.depth)
            issues.extend(
                CpnExpressionOperationError(
                    issue.code,
                    ("expressions", str(index)) + issue.path,
                    issue.diagnostic,
                )
                for issue in result.issues
            )
            if total_nodes > 4096:
                issues.append(
                    CpnExpressionOperationError(
                        CpnExpressionOperationErrorCode.EXPRESSION_TOO_MANY_NODES,
                        ("transition",),
                        "guard and output expressions exceed 4096 total nodes",
                    )
                )
                break
        return CpnExpressionBoundsValidationResult(
            total_nodes, maximum_depth, tuple(issues)
        )
