from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnExecutionProfileIdentity.__name__
        == "WorkflowCpnExecutionProfileIdentity"
    )
