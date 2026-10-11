from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnInputArcValidatorIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnInputArcValidatorIdentity.__name__ == "CpnInputArcValidatorIdentity"
    )
