"""Closed CPN expression collection operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ..grammar import CpnBindingVariableIdentity
from ..grammar import (
    CpnGuardExpression,
)
from .expressions import (
    CpnExpressionVariableCollectionInput,
    CpnExpressionVariableCollector,
)
from .guards import (
    CpnGuardExpressionCollectionInput,
    CpnGuardExpressionCollector,
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
