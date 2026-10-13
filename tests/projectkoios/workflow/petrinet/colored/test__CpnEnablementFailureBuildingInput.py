from projectkoios.workflow.petrinet.colored.enablement.failure_building import (
    CpnEnablementFailureBuildingInput,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnEnablementFailureBuildingInput.__name__
        == "CpnEnablementFailureBuildingInput"
    )
