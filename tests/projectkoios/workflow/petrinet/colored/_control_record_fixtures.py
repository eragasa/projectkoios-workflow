"""Small exact control-record fixtures for owner-operation tests."""

from projectkoios.workflow.petrinet.colored.bindings import (
    CpnBinding,
    CpnBindingAssignment,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
    CpnControlRecord,
    CpnControlRecordField,
    CpnControlRecordFieldDefinition,
    CpnControlRecordFieldIdentity,
    CpnControlRecordTypeDefinition,
    CpnControlRecordTypeIdentity,
)


def record_types() -> tuple[CpnControlRecordTypeDefinition, ...]:
    """Return nested and root schemas in lexical type order."""
    nested = CpnControlRecordTypeDefinition(
        CpnControlRecordTypeIdentity("fixture/nested:1"),
        1,
        (
            CpnControlRecordFieldDefinition(
                CpnControlRecordFieldIdentity("completed"),
                CpnValueKind.BOOLEAN,
            ),
        ),
    )
    root = CpnControlRecordTypeDefinition(
        CpnControlRecordTypeIdentity("fixture/root:1"),
        1,
        (
            CpnControlRecordFieldDefinition(
                CpnControlRecordFieldIdentity("child"),
                record_type_identity=nested.identity,
            ),
            CpnControlRecordFieldDefinition(
                CpnControlRecordFieldIdentity("task_id"),
                CpnValueKind.STRING,
                reference_role_identity="fixture-task",
            ),
        ),
    )
    return (nested, root)


def record() -> CpnControlRecord:
    """Return one exact bounded root record."""
    nested_type, root_type = record_types()
    nested = CpnControlRecord(
        nested_type.identity,
        (
            CpnControlRecordField(
                CpnControlRecordFieldIdentity("completed"),
                CpnValue(CpnValueKind.BOOLEAN, True),
            ),
        ),
    )
    return CpnControlRecord(
        root_type.identity,
        (
            CpnControlRecordField(
                CpnControlRecordFieldIdentity("child"),
                CpnValue(CpnValueKind.CONTROL_RECORD, nested),
            ),
            CpnControlRecordField(
                CpnControlRecordFieldIdentity("task_id"),
                CpnValue(CpnValueKind.STRING, "task-1"),
            ),
        ),
    )


def binding() -> CpnBinding:
    """Return one binding containing the exact fixture record."""
    from projectkoios.workflow.petrinet.colored.definitions import (
        CpnTransitionIdentity,
    )

    return CpnBinding(
        CpnTransitionIdentity("transition"),
        (
            CpnBindingAssignment(
                CpnBindingVariableIdentity("record"),
                CpnValue(CpnValueKind.CONTROL_RECORD, record()),
            ),
        ),
    )
