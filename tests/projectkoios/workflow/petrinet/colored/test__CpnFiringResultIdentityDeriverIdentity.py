from projectkoios.workflow.petrinet.colored.firing.identity_derivation import (
    CpnFiringResultIdentityDeriverIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnFiringResultIdentityDeriverIdentity.__name__
        == "CpnFiringResultIdentityDeriverIdentity"
    )
