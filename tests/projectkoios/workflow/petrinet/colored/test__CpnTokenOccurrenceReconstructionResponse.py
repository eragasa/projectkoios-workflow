from projectkoios.workflow.petrinet.colored.firing.occurrence_reconstruction import (
    CpnTokenOccurrenceReconstructionResponse,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructionResponse.__name__
        == "CpnTokenOccurrenceReconstructionResponse"
    )
