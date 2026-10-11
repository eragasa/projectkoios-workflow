from projectkoios.workflow.petrinet.colored.enablement import (
    CpnEnablementFailureBuildingInput,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnEnablementFailureBuildingInput.__name__
        == "CpnEnablementFailureBuildingInput"
    )
