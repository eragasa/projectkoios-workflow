from projectkoios.workflow.petrinet.colored.children.exports.canonical import (
    WorkflowChildDefinitionExporter,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildDefinitionExporter.__name__
        == "WorkflowChildDefinitionExporter"
    )
