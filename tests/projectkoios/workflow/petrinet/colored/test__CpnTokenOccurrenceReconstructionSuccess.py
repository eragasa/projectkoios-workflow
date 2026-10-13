from projectkoios.workflow.petrinet.colored.firing.occurrence_reconstruction import (
    CpnTokenOccurrenceReconstructionSuccess,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructionSuccess.__name__
        == "CpnTokenOccurrenceReconstructionSuccess"
    )
