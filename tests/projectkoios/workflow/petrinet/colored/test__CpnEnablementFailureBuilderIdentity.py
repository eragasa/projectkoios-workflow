from projectkoios.workflow.petrinet.colored.enablement import (
    CpnEnablementFailureBuilderIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnEnablementFailureBuilderIdentity.__name__
        == "CpnEnablementFailureBuilderIdentity"
    )
