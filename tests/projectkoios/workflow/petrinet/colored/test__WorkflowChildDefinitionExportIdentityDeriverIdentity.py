from projectkoios.workflow.petrinet.colored.children.exports.canonical import (
    WorkflowChildDefinitionExportIdentityDeriverIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildDefinitionExportIdentityDeriverIdentity.__name__
        == "WorkflowChildDefinitionExportIdentityDeriverIdentity"
    )
