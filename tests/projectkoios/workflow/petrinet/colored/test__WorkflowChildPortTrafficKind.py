from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowChildPortTrafficKind,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildPortTrafficKind.__name__ == "WorkflowChildPortTrafficKind"
    )
