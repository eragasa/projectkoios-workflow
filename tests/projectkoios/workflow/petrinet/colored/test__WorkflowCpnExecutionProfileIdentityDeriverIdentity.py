from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileIdentityDeriverIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnExecutionProfileIdentityDeriverIdentity.__name__
        == "WorkflowCpnExecutionProfileIdentityDeriverIdentity"
    )
