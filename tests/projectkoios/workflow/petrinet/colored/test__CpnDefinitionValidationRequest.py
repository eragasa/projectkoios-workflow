from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnDefinitionValidationRequest,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        CpnDefinitionValidationRequest.__name__
        == "CpnDefinitionValidationRequest"
    )
