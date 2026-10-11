"""Direct tests for closed generic control-record field projection."""

import pytest

from projectkoios.workflow.petrinet.colored.expressions.errors import (
    CpnExpressionOperationError,
    CpnExpressionOperationErrorCode,
)
from projectkoios.workflow.petrinet.colored.expressions.projection import (
    CpnFieldProjectionInput,
    CpnFieldProjector,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
    CpnControlRecordFieldIdentity,
)

from _control_record_fixtures import record


def test_execute__projects_exact_nested_path() -> None:
    """A declared path returns the exact retained Boolean value."""
    result = CpnFieldProjector().execute(
        CpnFieldProjectionInput(
            CpnValue(CpnValueKind.CONTROL_RECORD, record()),
            (
                CpnControlRecordFieldIdentity("child"),
                CpnControlRecordFieldIdentity("completed"),
            ),
        )
    )
    assert result.value == CpnValue(CpnValueKind.BOOLEAN, True)


def test_execute__rejects_unrelated_field() -> None:
    """Projection does not treat an unrelated identity as a match."""
    with pytest.raises(CpnExpressionOperationError) as caught:
        CpnFieldProjector().execute(
            CpnFieldProjectionInput(
                CpnValue(CpnValueKind.CONTROL_RECORD, record()),
                (CpnControlRecordFieldIdentity("unrelated"),),
            )
        )
    assert (
        caught.value.code
        is CpnExpressionOperationErrorCode.UNKNOWN_PROJECTED_FIELD
    )
