from projectkoios.workflow.petrinet.colored.children.exports.definition import (
    WorkflowChildDefinitionExportClosure,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildDefinitionExportClosure.__name__
        == "WorkflowChildDefinitionExportClosure"
    )
