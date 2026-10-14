"""Direct tests for bounded acyclic expression-structure validation."""

from projectkoios.workflow.petrinet.colored.expressions.errors import (
    CpnExpressionOperationErrorCode,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from projectkoios.workflow.petrinet.colored.expressions.validation.structure import (
    CpnExpressionStructureValidationInput,
    CpnExpressionStructureValidator,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnControlRecordFieldIdentity,
)

SUT = CpnExpressionStructureValidator


def test_execute__rejects_adversarial_expression_cycle() -> None:
    """A bypass-constructed cycle closes without recursion or nontermination."""
    expression = CpnValueExpression(
        CpnValueExpressionKind.VARIABLE,
        variable_identity=CpnBindingVariableIdentity("value"),
    )
    object.__setattr__(
        expression, "kind", CpnValueExpressionKind.FIELD_PROJECTION
    )
    object.__setattr__(expression, "literal", None)
    object.__setattr__(expression, "variable_identity", None)
    object.__setattr__(expression, "base_expression", expression)
    object.__setattr__(
        expression,
        "field_path",
        (CpnControlRecordFieldIdentity("again"),),
    )
    result = SUT().execute(
        CpnExpressionStructureValidationInput(expression, ())
    )
    assert CpnExpressionOperationErrorCode.CYCLIC_EXPRESSION in {
        item.code for item in result.issues
    }
