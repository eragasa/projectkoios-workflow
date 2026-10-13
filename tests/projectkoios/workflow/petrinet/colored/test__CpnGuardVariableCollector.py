import pytest

from projectkoios.workflow.petrinet.colored.expressions.collection import (
    CpnGuardVariableCollector,
)

SUT = CpnGuardVariableCollector


def test_public_action__is_final_slotted_and_rejects_untyped_input() -> None:
    assert SUT.__final__ is True
    assert SUT.__slots__ == ()
    with pytest.raises(TypeError):
        SUT().execute(None)  # type: ignore[arg-type]
