from projectkoios.workflow.petrinet.colored.firing import (
    CpnFiringFailureBuilderIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnFiringFailureBuilderIdentity.__name__
        == "CpnFiringFailureBuilderIdentity"
    )
