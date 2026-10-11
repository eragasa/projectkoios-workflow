from projectkoios.workflow.petrinet.colored.firing import (
    CpnTokenOccurrenceReconstructionRequest,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructionRequest.__name__
        == "CpnTokenOccurrenceReconstructionRequest"
    )
