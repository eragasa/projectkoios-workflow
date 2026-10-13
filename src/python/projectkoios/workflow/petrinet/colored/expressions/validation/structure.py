"""Closed CPN expression validation operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ...values import (
    CpnControlRecordTypeDefinition,
)
from ..grammar import (
    CpnValueExpression,
    CpnValueExpressionKind,
)
from ..errors import (
    CpnExpressionOperationError,
    CpnExpressionOperationErrorCode,
)


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
