from projectkoios.workflow.petrinet.colored.closure_validation import (
    WorkflowCpnClosureCorrelationIssueCode,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnClosureCorrelationIssueCode.__name__
        == "WorkflowCpnClosureCorrelationIssueCode"
    )
