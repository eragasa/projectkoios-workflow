from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnInputArcValidationResponse,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnInputArcValidationResponse.__name__
        == "CpnInputArcValidationResponse"
    )
