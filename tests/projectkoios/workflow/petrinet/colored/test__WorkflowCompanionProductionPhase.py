from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowCompanionProductionPhase,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCompanionProductionPhase.__name__
        == "WorkflowCompanionProductionPhase"
    )
