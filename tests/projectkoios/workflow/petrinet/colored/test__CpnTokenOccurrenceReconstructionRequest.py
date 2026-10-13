from projectkoios.workflow.petrinet.colored.firing.occurrence_reconstruction import (
    CpnTokenOccurrenceReconstructionRequest,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructionRequest.__name__
        == "CpnTokenOccurrenceReconstructionRequest"
    )
