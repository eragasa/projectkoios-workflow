"""Closed CPN expression collection operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ..grammar import CpnBindingVariableIdentity
from ..grammar import (
    CpnValueExpression,
    CpnValueExpressionKind,
)
from ..errors import (
    CpnExpressionOperationError,
    CpnExpressionOperationErrorCode,
)


@dataclass(frozen=True, slots=True)
class CpnExpressionVariableCollectorIdentity:
    """Identity of exact expression-variable collection semantics."""

    value: str = "projectkoios.workflow.cpn.expression-variable-collector:0.1"


@dataclass(frozen=True, slots=True)
class CpnExpressionVariableCollectionInput:
    """One expression whose whole-variable leaves are requested."""

    expression: CpnValueExpression

    def __post_init__(self) -> None:
        if type(self.expression) is not CpnValueExpression:
            raise TypeError("expression must be CpnValueExpression")


@dataclass(frozen=True, slots=True)
class CpnExpressionVariableCollectionResult:
    """Variables in deterministic expression-tree traversal order."""

    variable_identities: tuple[CpnBindingVariableIdentity, ...]

    def __post_init__(self) -> None:
        if type(self.variable_identities) is not tuple or any(
            type(item) is not CpnBindingVariableIdentity
            for item in self.variable_identities
        ):
            raise TypeError(
                "variable_identities must be a tuple of "
                "CpnBindingVariableIdentity"
            )


@final
class CpnExpressionVariableCollector:
    """Directly enumerate only declared whole-variable expression leaves."""

    __slots__ = ()

    @property
    def identity(self) -> CpnExpressionVariableCollectorIdentity:
        """Return the exact collection semantics identity."""
        return CpnExpressionVariableCollectorIdentity()

    def execute(
        self, collection_input: CpnExpressionVariableCollectionInput
    ) -> CpnExpressionVariableCollectionResult:
        """Return variables without evaluating or traversing runtime objects."""
        if type(collection_input) is not CpnExpressionVariableCollectionInput:
            raise TypeError(
                "collection_input must be CpnExpressionVariableCollectionInput"
            )
        variables: list[CpnBindingVariableIdentity] = []
        stack: list[tuple[CpnValueExpression, frozenset[int], int]] = [
            (collection_input.expression, frozenset(), 0)
        ]
        nodes = 0
        while stack:
            expression, ancestors, depth = stack.pop()
            marker = id(expression)
            if marker in ancestors:
                raise CpnExpressionOperationError(
                    CpnExpressionOperationErrorCode.CYCLIC_EXPRESSION,
                    (),
                    "expression graph must be an acyclic tree",
                )
            nodes += 1
            if depth > 64:
                raise CpnExpressionOperationError(
                    CpnExpressionOperationErrorCode.EXPRESSION_TOO_DEEP,
                    (),
                    "expression tree exceeds depth 64",
                )
            if nodes > 4096:
                raise CpnExpressionOperationError(
                    CpnExpressionOperationErrorCode.EXPRESSION_TOO_MANY_NODES,
                    (),
                    "expression tree exceeds 4096 nodes",
                )
            descendants = ancestors | {marker}
            if expression.kind is CpnValueExpressionKind.VARIABLE:
                assert expression.variable_identity is not None
                variables.append(expression.variable_identity)
            elif expression.kind is (CpnValueExpressionKind.FIELD_PROJECTION):
                assert expression.base_expression is not None
                stack.append(
                    (expression.base_expression, descendants, depth + 1)
                )
            elif expression.kind is (
                CpnValueExpressionKind.CONTROL_RECORD_CONSTRUCTOR
            ):
                stack.extend(
                    (field.expression, descendants, depth + 1)
                    for field in reversed(expression.constructor_fields)
                )
        return CpnExpressionVariableCollectionResult(tuple(variables))
