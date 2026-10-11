from projectkoios.workflow.petrinet.colored.children.exports.canonical import (
    WorkflowChildDefinitionExportIdentityDerivationInput,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildDefinitionExportIdentityDerivationInput.__name__
        == "WorkflowChildDefinitionExportIdentityDerivationInput"
    )
