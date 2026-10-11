from projectkoios.workflow.petrinet.colored.markings import (
    CpnTokenOrderingPolicy,
)


def test_public_contract__is_declared() -> None:
    assert CpnTokenOrderingPolicy.__name__ == "CpnTokenOrderingPolicy"
