from projectkoios.workflow.petrinet.colored.children.exports.canonical import (
    WorkflowChildDefinitionExportInput,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildDefinitionExportInput.__name__
        == "WorkflowChildDefinitionExportInput"
    )
