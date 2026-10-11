from projectkoios.workflow.petrinet.colored.firing import (
    CpnTokenOccurrenceReconstructor,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructor.__name__
        == "CpnTokenOccurrenceReconstructor"
    )
