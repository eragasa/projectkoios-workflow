from dataclasses import replace

from _deployment_fixtures import deployment_descriptor
from projectkoios.workflow.petrinet.colored.deployments.bindings import (
    WorkflowDeploymentBindingKind,
)


def test_constructor__derives_identity_from_deployment_content() -> None:
    source = deployment_descriptor(WorkflowDeploymentBindingKind.PROVIDER)
    changed_capability = replace(
        source.capability, protocol_requirement_identities=("protocol:2",)
    )
    assert (
        source.identity
        != replace(
            source,
            capability=changed_capability,
            protocol_identity="protocol:2",
        ).identity
    )
