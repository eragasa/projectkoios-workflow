"""Direct tests for bounded acyclic guard-expression collection."""

import pytest

from projectkoios.workflow.petrinet.colored.expressions.collection.guards import (
    CpnGuardExpressionCollectionInput,
    CpnGuardExpressionCollector,
)
from projectkoios.workflow.petrinet.colored.expressions.errors import (
    CpnExpressionOperationError,
    CpnExpressionOperationErrorCode,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnGuardExpression,
    CpnGuardOperator,
)

SUT = CpnGuardExpressionCollector


def test_execute__rejects_adversarial_guard_cycle() -> None:
    """A bypass-constructed guard cycle closes without nontermination."""
    guard = CpnGuardExpression(CpnGuardOperator.TRUE)
    object.__setattr__(guard, "operator", CpnGuardOperator.ALL)
    object.__setattr__(guard, "operands", (guard,))
    with pytest.raises(CpnExpressionOperationError) as caught:
        SUT().execute(CpnGuardExpressionCollectionInput(guard))
    assert (
        caught.value.code is CpnExpressionOperationErrorCode.CYCLIC_EXPRESSION
    )
