from projectkoios.workflow.petrinet.colored.markings import (
    CpnTokenOrderingInput,
)


def test_public_contract__is_declared() -> None:
    assert CpnTokenOrderingInput.__name__ == "CpnTokenOrderingInput"
