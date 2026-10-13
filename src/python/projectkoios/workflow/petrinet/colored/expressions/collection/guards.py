"""Closed CPN expression collection operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ..grammar import (
    CpnGuardExpression,
    CpnValueExpression,
)
from ..errors import (
    CpnExpressionOperationError,
    CpnExpressionOperationErrorCode,
)


@dataclass(frozen=True, slots=True)
class CpnGuardExpressionCollectorIdentity:
    """Identity of bounded acyclic guard-expression collection semantics."""

    value: str = "projectkoios.workflow.cpn.guard-expression-collector:0.1"


@dataclass(frozen=True, slots=True)
class CpnGuardExpressionCollectionInput:
    """One closed guard whose value-expression nodes are requested."""

    guard: CpnGuardExpression

    def __post_init__(self) -> None:
        if type(self.guard) is not CpnGuardExpression:
            raise TypeError("guard must be CpnGuardExpression")


@dataclass(frozen=True, slots=True)
class CpnGuardExpressionCollectionResult:
    """Value expressions and exact bounded guard-tree dimensions."""

    expressions: tuple[CpnValueExpression, ...]
    guard_node_count: int
    maximum_guard_depth: int

    def __post_init__(self) -> None:
        if type(self.expressions) is not tuple or any(
            type(item) is not CpnValueExpression for item in self.expressions
        ):
            raise TypeError("expressions must be a tuple of CpnValueExpression")
        for name in ("guard_node_count", "maximum_guard_depth"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise TypeError(f"{name} must be a nonnegative integer")


@final
class CpnGuardExpressionCollector:
    """Directly collect value expressions from one bounded acyclic guard."""

    __slots__ = ()

    @property
    def identity(self) -> CpnGuardExpressionCollectorIdentity:
        """Return exact collection semantics identity."""
        return CpnGuardExpressionCollectorIdentity()

    def execute(
        self, collection_input: CpnGuardExpressionCollectionInput
    ) -> CpnGuardExpressionCollectionResult:
        """Traverse guard nodes without recursion or expression evaluation."""
        if type(collection_input) is not CpnGuardExpressionCollectionInput:
            raise TypeError(
                "collection_input must be CpnGuardExpressionCollectionInput"
            )
        expressions: list[CpnValueExpression] = []
        stack: list[tuple[CpnGuardExpression, frozenset[int], int]] = [
            (collection_input.guard, frozenset(), 0)
        ]
        nodes = 0
        maximum_depth = 0
        while stack:
            guard, ancestors, depth = stack.pop()
            marker = id(guard)
            if marker in ancestors:
                raise CpnExpressionOperationError(
                    CpnExpressionOperationErrorCode.CYCLIC_EXPRESSION,
                    (),
                    "guard graph must be an acyclic tree",
                )
            nodes += 1
            maximum_depth = max(maximum_depth, depth)
            if depth > 64:
                raise CpnExpressionOperationError(
                    CpnExpressionOperationErrorCode.EXPRESSION_TOO_DEEP,
                    (),
                    "guard tree exceeds depth 64",
                )
            if nodes > 4096:
                raise CpnExpressionOperationError(
                    CpnExpressionOperationErrorCode.EXPRESSION_TOO_MANY_NODES,
                    (),
                    "guard tree exceeds 4096 nodes",
                )
            if guard.left is not None:
                expressions.append(guard.left)
            if guard.right is not None:
                expressions.append(guard.right)
            descendants = ancestors | {marker}
            stack.extend(
                (operand, descendants, depth + 1)
                for operand in reversed(guard.operands)
            )
        return CpnGuardExpressionCollectionResult(
            tuple(expressions), nodes, maximum_depth
        )
