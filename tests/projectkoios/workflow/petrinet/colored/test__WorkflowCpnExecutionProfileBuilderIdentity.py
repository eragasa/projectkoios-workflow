from projectkoios.workflow.petrinet.colored.profiles.defaults import (
    WorkflowCpnExecutionProfileBuilderIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnExecutionProfileBuilderIdentity.__name__
        == "WorkflowCpnExecutionProfileBuilderIdentity"
    )
