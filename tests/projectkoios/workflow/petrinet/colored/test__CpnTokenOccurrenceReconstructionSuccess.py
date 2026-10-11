from projectkoios.workflow.petrinet.colored.firing import (
    CpnTokenOccurrenceReconstructionSuccess,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructionSuccess.__name__
        == "CpnTokenOccurrenceReconstructionSuccess"
    )
