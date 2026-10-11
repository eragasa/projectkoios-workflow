from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowChildPortDirection,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert WorkflowChildPortDirection.__name__ == "WorkflowChildPortDirection"
