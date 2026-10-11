from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnOutputArcValidationRequest,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnOutputArcValidationRequest.__name__
        == "CpnOutputArcValidationRequest"
    )
