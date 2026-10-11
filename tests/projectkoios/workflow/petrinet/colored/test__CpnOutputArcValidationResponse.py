from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnOutputArcValidationResponse,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnOutputArcValidationResponse.__name__
        == "CpnOutputArcValidationResponse"
    )
