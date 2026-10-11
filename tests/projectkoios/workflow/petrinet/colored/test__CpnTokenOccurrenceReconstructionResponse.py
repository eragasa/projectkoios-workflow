from projectkoios.workflow.petrinet.colored.firing import (
    CpnTokenOccurrenceReconstructionResponse,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructionResponse.__name__
        == "CpnTokenOccurrenceReconstructionResponse"
    )
