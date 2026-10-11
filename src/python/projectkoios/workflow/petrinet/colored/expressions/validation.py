"""Closed CPN expression validation operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ..values import (
    CpnControlRecordTypeDefinition,
)
from .grammar import (
    CpnGuardExpression,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from .collection import (
    CpnGuardExpressionCollectionInput,
    CpnGuardExpressionCollector,
)
from .errors import CpnExpressionOperationError, CpnExpressionOperationErrorCode


@dataclass(frozen=True, slots=True)
class CpnExpressionStructureValidatorIdentity:
    """Identity of exact expression depth, node, and constructor validation."""

    value: str = "projectkoios.workflow.cpn.expression-structure-validator:0.1"


@dataclass(frozen=True, slots=True)
class CpnExpressionStructureValidationInput:
    """One expression and exact retained record schemas."""

    expression: CpnValueExpression
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...]

    def __post_init__(self) -> None:
        if type(self.expression) is not CpnValueExpression:
            raise TypeError("expression must be CpnValueExpression")
        if type(self.type_definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.type_definitions
        ):
            raise TypeError(
                "type_definitions must be a tuple of "
                "CpnControlRecordTypeDefinition"
            )


@dataclass(frozen=True, slots=True)
class CpnExpressionStructureValidationResult:
    """Bounded expression counts and closed validation findings."""

    depth: int
    node_count: int
    issues: tuple[CpnExpressionOperationError, ...]

    @property
    def is_valid(self) -> bool:
        """Return whether the expression is structurally conforming."""
        return not self.issues


@final
class CpnExpressionStructureValidator:
    """Directly validate the four-variant value-expression tree."""

    __slots__ = ()

    @property
    def identity(self) -> CpnExpressionStructureValidatorIdentity:
        """Return the exact operation identity."""
        return CpnExpressionStructureValidatorIdentity()

    def execute(
        self, validation_input: CpnExpressionStructureValidationInput
    ) -> CpnExpressionStructureValidationResult:
        """Inspect every node without executing an expression."""
        if type(validation_input) is not CpnExpressionStructureValidationInput:
            raise TypeError(
                "validation_input must be CpnExpressionStructureValidationInput"
            )
        known = {
            item.identity: item for item in validation_input.type_definitions
        }
        issues: list[CpnExpressionOperationError] = []
        maximum_depth = 0
        node_count = 0
        stack: list[
            tuple[
                CpnValueExpression,
                int,
                tuple[str, ...],
                frozenset[int],
            ]
        ] = [(validation_input.expression, 0, ("expression",), frozenset())]
        while stack:
            expression, depth, path, ancestors = stack.pop()
            marker = id(expression)
            if marker in ancestors:
                issues.append(
                    CpnExpressionOperationError(
                        CpnExpressionOperationErrorCode.CYCLIC_EXPRESSION,
                        path,
                        "expression graph must be an acyclic tree",
                    )
                )
                continue
            node_count += 1
            maximum_depth = max(maximum_depth, depth)
            if node_count > 4096:
                issues.append(
                    CpnExpressionOperationError(
                        CpnExpressionOperationErrorCode.EXPRESSION_TOO_MANY_NODES,
                        path,
                        "expression tree exceeds 4096 nodes",
                    )
                )
                break
            if depth > 64:
                issues.append(
                    CpnExpressionOperationError(
                        CpnExpressionOperationErrorCode.EXPRESSION_TOO_DEEP,
                        path,
                        "expression depth exceeds 64",
                    )
                )
                continue
            descendants = ancestors | {marker}
            if expression.kind is CpnValueExpressionKind.FIELD_PROJECTION:
                assert expression.base_expression is not None
                stack.append(
                    (
                        expression.base_expression,
                        depth + 1,
                        path + ("base",),
                        descendants,
                    )
                )
            elif expression.kind is (
                CpnValueExpressionKind.CONTROL_RECORD_CONSTRUCTOR
            ):
                assert expression.record_type_identity is not None
                definition = known.get(expression.record_type_identity)
                if definition is None:
                    issues.append(
                        CpnExpressionOperationError(
                            CpnExpressionOperationErrorCode.UNKNOWN_RECORD_TYPE,
                            path + ("record_type",),
                            "constructor references an unknown record type",
                        )
                    )
                elif tuple(
                    item.identity for item in expression.constructor_fields
                ) != tuple(item.identity for item in definition.fields):
                    issues.append(
                        CpnExpressionOperationError(
                            CpnExpressionOperationErrorCode.CONSTRUCTOR_FIELD_MISMATCH,
                            path + ("fields",),
                            "constructor fields differ from the retained schema",
                        )
                    )
                for field in reversed(expression.constructor_fields):
                    stack.append(
                        (
                            field.expression,
                            depth + 1,
                            path + ("fields", field.identity.value),
                            descendants,
                        )
                    )
        return CpnExpressionStructureValidationResult(
            maximum_depth, node_count, tuple(issues)
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
