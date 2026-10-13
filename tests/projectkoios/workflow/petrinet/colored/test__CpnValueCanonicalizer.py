"""Direct tests for finite iterative generic-value canonicalization."""

import pytest

from projectkoios.workflow.petrinet.colored.control.records.values.canonicalization import (
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
    CpnControlRecord,
    CpnControlRecordField,
    CpnControlRecordFieldIdentity,
    CpnControlRecordTypeIdentity,
)

SUT = CpnValueCanonicalizer


def cyclic_value() -> CpnValue:
    """Build adversarial cyclic state by bypassing immutable constructors."""
    record = object.__new__(CpnControlRecord)
    value = object.__new__(CpnValue)
    object.__setattr__(
        record, "type_identity", CpnControlRecordTypeIdentity("cycle")
    )
    object.__setattr__(value, "kind", CpnValueKind.CONTROL_RECORD)
    object.__setattr__(value, "value", record)
    object.__setattr__(
        record,
        "fields",
        (CpnControlRecordField(CpnControlRecordFieldIdentity("again"), value),),
    )
    return value


def test_execute__rejects_cyclic_adversarial_value_without_recursion_leak() -> (
    None
):
    """Canonicalization closes a cycle as ValueError, not RecursionError."""
    with pytest.raises(ValueError, match="cyclic control-record value"):
        SUT().execute(CpnValueCanonicalizationInput(cyclic_value()))
