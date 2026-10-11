from projectkoios.workflow.petrinet.colored.firing import (
    CpnSuccessorMarkingBuildingRequest,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnSuccessorMarkingBuildingRequest.__name__
        == "CpnSuccessorMarkingBuildingRequest"
    )
