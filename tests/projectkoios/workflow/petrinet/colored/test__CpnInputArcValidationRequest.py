from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnInputArcValidationRequest,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnInputArcValidationRequest.__name__ == "CpnInputArcValidationRequest"
    )
