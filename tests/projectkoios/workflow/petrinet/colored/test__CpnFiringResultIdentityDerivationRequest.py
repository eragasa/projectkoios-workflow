from projectkoios.workflow.petrinet.colored.firing.identity_derivation import (
    CpnFiringResultIdentityDerivationRequest,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnFiringResultIdentityDerivationRequest.__name__
        == "CpnFiringResultIdentityDerivationRequest"
    )
