from projectkoios.workflow.petrinet.colored.closure_validation import (
    WorkflowCpnClosureCorrelationResult,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnClosureCorrelationResult.__name__
        == "WorkflowCpnClosureCorrelationResult"
    )
