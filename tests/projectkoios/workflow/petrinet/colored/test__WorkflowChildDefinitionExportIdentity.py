from projectkoios.workflow.petrinet.colored.children.exports.definition import (
    WorkflowChildDefinitionExportIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildDefinitionExportIdentity.__name__
        == "WorkflowChildDefinitionExportIdentity"
    )
