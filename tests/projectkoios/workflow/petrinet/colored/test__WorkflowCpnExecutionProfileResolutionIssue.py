from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileResolutionIssue,
)


def test_constructor__retains_exact_component_mismatch() -> None:
    issue = WorkflowCpnExecutionProfileResolutionIssue(
        "transition_firer_identity", "retained", "supported"
    )
    assert issue.retained_identity == "retained"
    assert issue.supported_identity == "supported"
