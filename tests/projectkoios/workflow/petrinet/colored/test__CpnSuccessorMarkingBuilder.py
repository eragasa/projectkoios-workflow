from projectkoios.workflow.petrinet.colored.firing import (
    CpnSuccessorMarkingBuilder,
)


def test_public_contract__is_declared() -> None:
    assert CpnSuccessorMarkingBuilder.__name__ == "CpnSuccessorMarkingBuilder"
