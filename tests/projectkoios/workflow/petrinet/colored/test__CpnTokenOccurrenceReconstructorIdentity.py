from projectkoios.workflow.petrinet.colored.firing.occurrence_reconstruction import (
    CpnTokenOccurrenceReconstructorIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructorIdentity.__name__
        == "CpnTokenOccurrenceReconstructorIdentity"
    )
