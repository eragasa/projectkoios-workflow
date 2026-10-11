"""Direct tests for aggregate per-transition expression bounds."""

from projectkoios.workflow.petrinet.colored.expressions.errors import (
    CpnExpressionOperationErrorCode,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnGuardExpression,
    CpnGuardOperator,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from projectkoios.workflow.petrinet.colored.expressions.validation import (
    CpnExpressionBoundsValidationInput,
    CpnExpressionBoundsValidator,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
)

SUT = CpnExpressionBoundsValidator


def literal() -> CpnValueExpression:
    """Return one depth-zero node."""
    return CpnValueExpression(
        CpnValueExpressionKind.LITERAL,
        literal=CpnValue(CpnValueKind.NONE, None),
    )


def test_execute__accepts_exact_4096_transition_nodes() -> None:
    """One guard plus 4095 output nodes is exactly admitted."""
    result = SUT().execute(
        CpnExpressionBoundsValidationInput(
            CpnGuardExpression(CpnGuardOperator.TRUE),
            tuple(literal() for _ in range(4095)),
            (),
        )
    )
    assert result.total_node_count == 4096
    assert result.is_valid


def test_execute__rejects_one_node_beyond_transition_bound() -> None:
    """One guard plus 4096 output nodes closes at 4097."""
    result = SUT().execute(
        CpnExpressionBoundsValidationInput(
            CpnGuardExpression(CpnGuardOperator.TRUE),
            tuple(literal() for _ in range(4096)),
            (),
        )
    )
    assert result.total_node_count == 4097
    assert CpnExpressionOperationErrorCode.EXPRESSION_TOO_MANY_NODES in {
        item.code for item in result.issues
    }
