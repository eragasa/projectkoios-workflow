"""Direct tests for closed generic control-record construction."""

import pytest

from projectkoios.workflow.petrinet.colored.expressions.construction import (
    CpnControlRecordConstructionInput,
    CpnControlRecordConstructor,
)
from projectkoios.workflow.petrinet.colored.expressions.errors import (
    CpnExpressionOperationError,
    CpnExpressionOperationErrorCode,
)

from _control_record_fixtures import record, record_types


def test_execute__constructs_exact_schema() -> None:
    """Exact fields produce the exact typed record."""
    value = record()
    result = CpnControlRecordConstructor().execute(
        CpnControlRecordConstructionInput(
            value.type_identity, value.fields, record_types()
        )
    )
    assert result.record == value


def test_execute__rejects_missing_field() -> None:
    """Construction never repairs an incomplete owner mapping."""
    value = record()
    with pytest.raises(CpnExpressionOperationError) as caught:
        CpnControlRecordConstructor().execute(
            CpnControlRecordConstructionInput(
                value.type_identity, value.fields[:-1], record_types()
            )
        )
    assert (
        caught.value.code
        is CpnExpressionOperationErrorCode.CONSTRUCTOR_FIELD_MISMATCH
    )
