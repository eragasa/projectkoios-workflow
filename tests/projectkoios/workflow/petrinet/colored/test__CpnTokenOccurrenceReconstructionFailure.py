from projectkoios.workflow.petrinet.colored.firing import (
    CpnTokenOccurrenceReconstructionFailure,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOccurrenceReconstructionFailure.__name__
        == "CpnTokenOccurrenceReconstructionFailure"
    )
