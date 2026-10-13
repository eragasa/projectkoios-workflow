from projectkoios.workflow.petrinet.colored.firing.failure_building import (
    CpnFiringFailureBuilderIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnFiringFailureBuilderIdentity.__name__
        == "CpnFiringFailureBuilderIdentity"
    )
