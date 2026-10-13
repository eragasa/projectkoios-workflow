from projectkoios.workflow.petrinet.colored.firing.occurrence_reconstruction import (
    CpnTokenOccurrenceReconstructor,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructor.__name__
        == "CpnTokenOccurrenceReconstructor"
    )
