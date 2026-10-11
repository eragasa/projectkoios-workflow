from dataclasses import replace

from projectkoios.workflow.petrinet.colored.profiles.defaults import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
    WorkflowCpnExecutionProfileResolutionRequest,
    WorkflowCpnExecutionProfileResolver,
)


def test_execute__resolves_every_retained_component() -> None:
    profile = WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )
    result = WorkflowCpnExecutionProfileResolver().execute(
        WorkflowCpnExecutionProfileResolutionRequest(profile)
    )
    assert result.is_available
    assert result.issues == ()


def test_execute__reports_each_unavailable_component() -> None:
    profile = WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )
    changed = replace(
        profile,
        canonical_binding_representation_identity="unsupported-binding",
        transition_firer_identity="unsupported-firer",
    )
    result = WorkflowCpnExecutionProfileResolver().execute(
        WorkflowCpnExecutionProfileResolutionRequest(changed)
    )
    assert tuple(item.component_name for item in result.issues) == (
        "canonical_binding_representation_identity",
        "transition_firer_identity",
    )
