from projectkoios.workflow.petrinet.colored.children.exports.canonical import (
    WorkflowChildDefinitionExportIdentityDeriver,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildDefinitionExportIdentityDeriver.__name__
        == "WorkflowChildDefinitionExportIdentityDeriver"
    )
