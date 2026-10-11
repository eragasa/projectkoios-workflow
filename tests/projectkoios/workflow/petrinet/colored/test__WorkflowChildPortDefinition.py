from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowChildPortDefinition,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert WorkflowChildPortDefinition.__name__ == "WorkflowChildPortDefinition"
