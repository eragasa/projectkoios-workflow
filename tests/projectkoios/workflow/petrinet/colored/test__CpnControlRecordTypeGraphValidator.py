"""Direct tests for retained control-record type-graph validation."""

from projectkoios.workflow.petrinet.colored.control.records.findings import (
    CpnControlRecordValidationIssueCode,
)
from projectkoios.workflow.petrinet.colored.control.records.types.graph import (
    CpnControlRecordTypeGraphValidationInput,
    CpnControlRecordTypeGraphValidator,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnControlRecordFieldDefinition,
    CpnControlRecordFieldIdentity,
    CpnControlRecordTypeDefinition,
    CpnControlRecordTypeIdentity,
)

from _control_record_fixtures import record_types


def test_execute__accepts_acyclic_graph() -> None:
    """The exact retained fixture graph is valid."""
    result = CpnControlRecordTypeGraphValidator().execute(
        CpnControlRecordTypeGraphValidationInput(record_types())
    )
    assert result.is_valid


def test_execute__rejects_cycle() -> None:
    """Mutual record references are rejected without traversal recursion."""
    one = CpnControlRecordTypeIdentity("one")
    two = CpnControlRecordTypeIdentity("two")
    definitions = (
        CpnControlRecordTypeDefinition(
            one,
            1,
            (
                CpnControlRecordFieldDefinition(
                    CpnControlRecordFieldIdentity("two"),
                    record_type_identity=two,
                ),
            ),
        ),
        CpnControlRecordTypeDefinition(
            two,
            1,
            (
                CpnControlRecordFieldDefinition(
                    CpnControlRecordFieldIdentity("one"),
                    record_type_identity=one,
                ),
            ),
        ),
    )
    result = CpnControlRecordTypeGraphValidator().execute(
        CpnControlRecordTypeGraphValidationInput(definitions)
    )
    assert CpnControlRecordValidationIssueCode.CYCLIC_TYPE_GRAPH in {
        item.code for item in result.issues
    }
