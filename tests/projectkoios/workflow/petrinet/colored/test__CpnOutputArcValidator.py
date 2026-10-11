from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnOutputArcValidator,
)


def test_public_contract__is_declared() -> None:
    assert CpnOutputArcValidator.__name__ == "CpnOutputArcValidator"
