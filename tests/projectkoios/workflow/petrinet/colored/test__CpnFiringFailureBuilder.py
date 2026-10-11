from projectkoios.workflow.petrinet.colored.firing import (
    CpnFiringFailureBuilder,
)


def test_public_contract__is_declared() -> None:
    assert CpnFiringFailureBuilder.__name__ == "CpnFiringFailureBuilder"
