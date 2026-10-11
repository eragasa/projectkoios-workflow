from projectkoios.workflow.petrinet.colored.firing import (
    CpnSuccessorMarkingBuilderIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnSuccessorMarkingBuilderIdentity.__name__
        == "CpnSuccessorMarkingBuilderIdentity"
    )
