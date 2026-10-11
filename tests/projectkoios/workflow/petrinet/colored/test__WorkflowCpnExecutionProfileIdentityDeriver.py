from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileIdentityDeriver,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnExecutionProfileIdentityDeriver.__name__
        == "WorkflowCpnExecutionProfileIdentityDeriver"
    )
