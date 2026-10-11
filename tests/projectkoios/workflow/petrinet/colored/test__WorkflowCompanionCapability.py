from dataclasses import replace

import pytest
from _deployment_fixtures import deployment_descriptor

from projectkoios.workflow.petrinet.colored.deployments.bindings import (
    WorkflowCompanionCapability,
    WorkflowDeploymentBindingKind,
)


def test_constructor__rejects_untyped_production_phase() -> None:
    source = deployment_descriptor(
        WorkflowDeploymentBindingKind.RESOLVER
    ).capability.companion_capabilities[0]
    with pytest.raises(TypeError, match="WorkflowCompanionProductionPhase"):
        replace(source, production_phase="unknown")  # type: ignore[arg-type]


def test_candidate_direct_module_contract__is_declared() -> None:
    assert WorkflowCompanionCapability.__name__ == "WorkflowCompanionCapability"
