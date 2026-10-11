from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnInputArcValidator,
)


def test_public_contract__is_declared() -> None:
    assert CpnInputArcValidator.__name__ == "CpnInputArcValidator"
