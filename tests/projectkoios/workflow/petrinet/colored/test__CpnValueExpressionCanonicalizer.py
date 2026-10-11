"""Direct tests for closed value-expression canonical transport."""

from projectkoios.workflow.petrinet.colored.canonical.expressions.values import (
    CpnValueExpressionCanonicalDecoder,
    CpnValueExpressionCanonicalDecodingInput,
    CpnValueExpressionCanonicalizationInput,
    CpnValueExpressionCanonicalizer,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnControlRecordFieldIdentity,
)

from _control_record_fixtures import record_types


def test_execute__projection_round_trips_exact_expression() -> None:
    """The closed projection grammar reconstructs exactly."""
    expression = CpnValueExpression(
        CpnValueExpressionKind.FIELD_PROJECTION,
        base_expression=CpnValueExpression(
            CpnValueExpressionKind.VARIABLE,
            variable_identity=CpnBindingVariableIdentity("record"),
        ),
        field_path=(CpnControlRecordFieldIdentity("task_id"),),
    )
    canonical_bytes = (
        CpnValueExpressionCanonicalizer()
        .execute(
            CpnValueExpressionCanonicalizationInput(expression, record_types())
        )
        .canonical_bytes
    )
    reconstructed = (
        CpnValueExpressionCanonicalDecoder()
        .execute(
            CpnValueExpressionCanonicalDecodingInput(
                canonical_bytes, record_types()
            )
        )
        .expression
    )
    assert reconstructed == expression
