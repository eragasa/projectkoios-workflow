from projectkoios.workflow.petrinet.colored.firing.failure_building import (
    CpnFiringFailureBuildingRequest,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnFiringFailureBuildingRequest.__name__
        == "CpnFiringFailureBuildingRequest"
    )
