from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileIdentityDerivationInput,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnExecutionProfileIdentityDerivationInput.__name__
        == "WorkflowCpnExecutionProfileIdentityDerivationInput"
    )
