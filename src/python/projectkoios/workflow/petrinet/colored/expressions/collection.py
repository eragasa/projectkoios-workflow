"""Closed CPN expression collection operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from .grammar import CpnBindingVariableIdentity
from .grammar import (
    CpnGuardExpression,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from .errors import CpnExpressionOperationError, CpnExpressionOperationErrorCode


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


@dataclass(frozen=True, slots=True)
class CpnGuardVariableCollectorIdentity:
    """Identity of bounded acyclic guard-variable collection semantics."""

    value: str = "projectkoios.workflow.cpn.guard-variable-collector:0.1"


@dataclass(frozen=True, slots=True)
class CpnGuardVariableCollectionInput:
    """One closed guard whose expression variables are requested."""

    guard: CpnGuardExpression

    def __post_init__(self) -> None:
        if type(self.guard) is not CpnGuardExpression:
            raise TypeError("guard must be CpnGuardExpression")


@dataclass(frozen=True, slots=True)
class CpnGuardVariableCollectionResult:
    """Variables in deterministic guard/expression traversal order."""

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
class CpnGuardVariableCollector:
    """Directly enumerate guard variables without hidden recursive traversal."""

    __slots__ = ()

    @property
    def identity(self) -> CpnGuardVariableCollectorIdentity:
        """Return exact collection semantics identity."""
        return CpnGuardVariableCollectorIdentity()

    def execute(
        self, collection_input: CpnGuardVariableCollectionInput
    ) -> CpnGuardVariableCollectionResult:
        """Traverse a bounded acyclic guard and its closed value expressions."""
        if type(collection_input) is not CpnGuardVariableCollectionInput:
            raise TypeError(
                "collection_input must be CpnGuardVariableCollectionInput"
            )
        expressions = (
            CpnGuardExpressionCollector()
            .execute(CpnGuardExpressionCollectionInput(collection_input.guard))
            .expressions
        )
        variables = tuple(
            variable
            for expression in expressions
            for variable in CpnExpressionVariableCollector()
            .execute(CpnExpressionVariableCollectionInput(expression))
            .variable_identities
        )
        return CpnGuardVariableCollectionResult(variables)
