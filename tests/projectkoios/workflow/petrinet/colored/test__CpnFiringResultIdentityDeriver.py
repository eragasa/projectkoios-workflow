from projectkoios.workflow.petrinet.colored.firing.identity_derivation import (
    CpnFiringResultIdentityDeriver,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnFiringResultIdentityDeriver.__name__
        == "CpnFiringResultIdentityDeriver"
    )
