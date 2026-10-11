from projectkoios.workflow.petrinet.colored.markings import (
    CpnTokenOrderingResult,
)


def test_public_contract__is_declared() -> None:
    assert CpnTokenOrderingResult.__name__ == "CpnTokenOrderingResult"
