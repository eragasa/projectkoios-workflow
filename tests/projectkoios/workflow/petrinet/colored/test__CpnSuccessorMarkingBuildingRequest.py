from projectkoios.workflow.petrinet.colored.firing.successor_marking import (
    CpnSuccessorMarkingBuildingRequest,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnSuccessorMarkingBuildingRequest.__name__
        == "CpnSuccessorMarkingBuildingRequest"
    )
