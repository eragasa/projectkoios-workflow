from projectkoios.workflow.petrinet.colored.enablement.failure_building import (
    CpnEnablementFailureBuilderIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnEnablementFailureBuilderIdentity.__name__
        == "CpnEnablementFailureBuilderIdentity"
    )
