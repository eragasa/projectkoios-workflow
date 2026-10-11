from projectkoios.workflow.petrinet.colored.children.exports.canonical import (
    WorkflowChildDefinitionExporterIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildDefinitionExporterIdentity.__name__
        == "WorkflowChildDefinitionExporterIdentity"
    )
