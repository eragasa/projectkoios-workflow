from projectkoios.workflow.petrinet.colored.expressions.errors import (
    CpnExpressionOperationErrorCode,
)

SUT = CpnExpressionOperationErrorCode


def test_public_enum__is_closed_unique_and_nonempty() -> None:
    values = tuple(item.value for item in SUT)
    assert values
    assert len(values) == len(set(values))
    assert all(type(value) is str and value for value in values)
