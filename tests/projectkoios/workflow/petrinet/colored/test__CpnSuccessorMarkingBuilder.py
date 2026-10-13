from projectkoios.workflow.petrinet.colored.firing.successor_marking import (
    CpnSuccessorMarkingBuilder,
)


def test_public_contract__is_declared() -> None:
    assert CpnSuccessorMarkingBuilder.__name__ == "CpnSuccessorMarkingBuilder"
