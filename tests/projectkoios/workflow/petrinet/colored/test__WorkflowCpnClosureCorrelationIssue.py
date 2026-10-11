from projectkoios.workflow.petrinet.colored.closure_validation import (
    WorkflowCpnClosureCorrelationIssue,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnClosureCorrelationIssue.__name__
        == "WorkflowCpnClosureCorrelationIssue"
    )
