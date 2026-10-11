from projectkoios.workflow.petrinet.colored.firing import (
    CpnFiringResultIdentityDeriverIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnFiringResultIdentityDeriverIdentity.__name__
        == "CpnFiringResultIdentityDeriverIdentity"
    )
