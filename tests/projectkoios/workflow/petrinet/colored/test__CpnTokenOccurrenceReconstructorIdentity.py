from projectkoios.workflow.petrinet.colored.firing import (
    CpnTokenOccurrenceReconstructorIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructorIdentity.__name__
        == "CpnTokenOccurrenceReconstructorIdentity"
    )
