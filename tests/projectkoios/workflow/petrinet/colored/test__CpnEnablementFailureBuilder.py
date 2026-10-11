from projectkoios.workflow.petrinet.colored.enablement import (
    CpnEnablementFailureBuilder,
)


def test_public_contract__is_declared() -> None:
    assert CpnEnablementFailureBuilder.__name__ == "CpnEnablementFailureBuilder"
