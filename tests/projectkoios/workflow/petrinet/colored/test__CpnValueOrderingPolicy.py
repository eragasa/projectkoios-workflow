"""Direct tests for finite iterative generic-value ordering."""

import pytest

from projectkoios.workflow.petrinet.colored.control.records.ordering import (
    CpnValueOrderingInput,
    CpnValueOrderingPolicy,
)

from test__CpnValueCanonicalizer import cyclic_value

SUT = CpnValueOrderingPolicy


def test_execute__rejects_cyclic_adversarial_value_without_recursion_leak() -> (
    None
):
    """Ordering closes a cycle as ValueError, not RecursionError."""
    with pytest.raises(ValueError, match="cyclic control-record value"):
        SUT().execute(CpnValueOrderingInput(cyclic_value()))
