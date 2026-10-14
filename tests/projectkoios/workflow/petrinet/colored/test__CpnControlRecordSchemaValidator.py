"""Direct tests for bounded exact control-record schema validation."""

from dataclasses import replace

from projectkoios.workflow.petrinet.colored.control.records.findings import (
    CpnControlRecordValidationIssueCode,
)
from projectkoios.workflow.petrinet.colored.control.records.schema import (
    CpnControlRecordSchemaValidationInput,
    CpnControlRecordSchemaValidator,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
    CpnControlRecordField,
    CpnControlRecordFieldIdentity,
)

from _control_record_fixtures import record, record_types


def test_execute__accepts_exact_nested_record() -> None:
    """An exact finite closed value is admitted."""
    result = CpnControlRecordSchemaValidator().execute(
        CpnControlRecordSchemaValidationInput(record(), record_types())
    )
    assert result.is_valid


def test_execute__rejects_wrong_kind_and_unknown_field_set() -> None:
    """Schema mismatch is closed and deterministic."""
    value = record()
    fields = value.fields + (
        CpnControlRecordField(
            CpnControlRecordFieldIdentity("alpha"),
            CpnValue(CpnValueKind.NONE, None),
        ),
    )
    result = CpnControlRecordSchemaValidator().execute(
        CpnControlRecordSchemaValidationInput(
            replace(value, fields=fields), record_types()
        )
    )
    assert {item.code for item in result.issues} >= {
        CpnControlRecordValidationIssueCode.NONCANONICAL_FIELD_ORDER,
        CpnControlRecordValidationIssueCode.FIELD_SET_MISMATCH,
    }


def test_execute__rejects_lone_surrogate_without_unicode_error_leak() -> None:
    """A non-UTF-8 string becomes one inspectable validation finding."""
    value = record()
    fields = (
        value.fields[0],
        replace(
            value.fields[1],
            value=CpnValue(CpnValueKind.STRING, "\ud800"),
        ),
    )
    result = CpnControlRecordSchemaValidator().execute(
        CpnControlRecordSchemaValidationInput(
            replace(value, fields=fields), record_types()
        )
    )
    assert CpnControlRecordValidationIssueCode.INVALID_UTF8_STRING in {
        item.code for item in result.issues
    }


def test_execute__enforces_string_bound() -> None:
    """A 4097-byte scalar is rejected one unit beyond its bound."""
    value = record()
    fields = (
        value.fields[0],
        replace(
            value.fields[1],
            value=CpnValue(CpnValueKind.STRING, "a" * 4097),
        ),
    )
    result = CpnControlRecordSchemaValidator().execute(
        CpnControlRecordSchemaValidationInput(
            replace(value, fields=fields), record_types()
        )
    )
    assert CpnControlRecordValidationIssueCode.STRING_TOO_LARGE in {
        item.code for item in result.issues
    }
