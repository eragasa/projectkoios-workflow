from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnOutputArcValidatorIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnOutputArcValidatorIdentity.__name__
        == "CpnOutputArcValidatorIdentity"
    )
