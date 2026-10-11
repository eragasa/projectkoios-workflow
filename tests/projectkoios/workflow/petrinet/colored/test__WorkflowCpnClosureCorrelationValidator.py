from projectkoios.workflow.petrinet.colored.closure_validation import (
    WorkflowCpnClosureCorrelationValidator,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnClosureCorrelationValidator.__name__
        == "WorkflowCpnClosureCorrelationValidator"
    )
