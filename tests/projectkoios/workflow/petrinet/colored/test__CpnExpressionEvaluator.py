"""Direct tests for bounded closed CPN expression evaluation."""

from projectkoios.workflow.petrinet.colored.expressions.evaluation import (
    CpnExpressionEvaluationInput,
    CpnExpressionEvaluator,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnValueExpression,
    CpnValueExpressionKind,
    CpnControlRecordConstructorField,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
    CpnControlRecordFieldIdentity,
)

from _control_record_fixtures import binding, record_types


def test_execute__evaluates_projection_without_owner_callbacks() -> None:
    """A field projection evaluates against only the admitted binding value."""
    variable = CpnValueExpression(
        CpnValueExpressionKind.VARIABLE,
        variable_identity=CpnBindingVariableIdentity("record"),
    )
    expression = CpnValueExpression(
        CpnValueExpressionKind.FIELD_PROJECTION,
        base_expression=variable,
        field_path=(
            CpnControlRecordFieldIdentity("child"),
            CpnControlRecordFieldIdentity("completed"),
        ),
    )
    result = CpnExpressionEvaluator().execute(
        CpnExpressionEvaluationInput(expression, binding(), record_types())
    )
    assert result.value == CpnValue(CpnValueKind.BOOLEAN, True)


def test_execute__evaluates_closed_constructor() -> None:
    """A constructor evaluates one expression per exact schema field."""
    nested_type = record_types()[0]
    expression = CpnValueExpression(
        CpnValueExpressionKind.CONTROL_RECORD_CONSTRUCTOR,
        record_type_identity=nested_type.identity,
        constructor_fields=(
            CpnControlRecordConstructorField(
                CpnControlRecordFieldIdentity("completed"),
                CpnValueExpression(
                    CpnValueExpressionKind.LITERAL,
                    literal=CpnValue(CpnValueKind.BOOLEAN, False),
                ),
            ),
        ),
    )
    result = CpnExpressionEvaluator().execute(
        CpnExpressionEvaluationInput(expression, binding(), record_types())
    )
    assert result.value.kind is CpnValueKind.CONTROL_RECORD
