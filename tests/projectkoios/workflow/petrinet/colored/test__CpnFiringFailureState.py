from projectkoios.workflow.petrinet.colored.firing.identity_derivation import (
    CpnFiringFailureState,
)


def test_public_contract__is_declared() -> None:
    assert CpnFiringFailureState.__name__ == "CpnFiringFailureState"
