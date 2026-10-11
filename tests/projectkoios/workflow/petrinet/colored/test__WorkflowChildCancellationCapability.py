from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowChildCancellationCapability,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildCancellationCapability.__name__
        == "WorkflowChildCancellationCapability"
    )
