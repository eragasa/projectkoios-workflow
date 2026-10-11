"""Direct tests for complete immutable child-definition exports."""

from _plan_fixtures import execution_plan_closure

from dataclasses import replace

import pytest

from projectkoios.workflow.petrinet.colored.children.exports.canonical import (
    WorkflowChildDefinitionExportInput,
    WorkflowChildDefinitionExporter,
)
from projectkoios.workflow.petrinet.colored.children.exports.definition import (
    WorkflowChildDefinitionExportClosure,
)
from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowChildCancellationCapability,
    WorkflowChildInterface,
    WorkflowChildPortDefinition,
    WorkflowChildPortDirection,
    WorkflowChildPortTrafficKind,
    WorkflowTerminalCompanionEvidenceRequirement,
    WorkflowTerminalDeliveryRequirement,
    WorkflowCompanionProductionPhase,
)
from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanIdentityDerivationInput,
    WorkflowExecutionPlanIdentityDeriver,
)


def closure() -> WorkflowChildDefinitionExportClosure:
    """Return one exact success export with one post-terminal companion."""
    terminal_port = WorkflowChildPortDefinition(
        "terminal-port",
        WorkflowChildPortDirection.OUTPUT,
        "terminal-place",
        "terminal-color",
        "primary-schema",
        "primary-codec",
        None,
        1,
        1,
        ("run-correlation",),
        WorkflowChildPortTrafficKind.TERMINAL,
        1,
    )
    companion = WorkflowTerminalCompanionEvidenceRequirement(
        0,
        "synthetic-companion-reference",
        "synthetic-owner",
        "synthetic-companion-schema",
        "synthetic-companion-codec",
        "application/vnd.projectkoios.synthetic-companion+json",
        4096,
        1,
        1,
        WorkflowCompanionProductionPhase.POST_TERMINAL_PRE_DELIVERY_RETAINED,
        "saved-state-correlation",
        1,
    )
    delivery = WorkflowTerminalDeliveryRequirement(
        "success",
        terminal_port.identity,
        "primary-schema",
        "primary-codec",
        (companion,),
        1,
        "primary-then-companions",
        "terminal-correlation",
        "synthetic-output-mapper",
        1,
    )
    interface = WorkflowChildInterface(
        input_ports=(),
        terminal_output_ports=(terminal_port,),
        admitted_terminal_classification_identities=("success",),
        terminal_delivery_requirements=(delivery,),
        cancellation_capability=WorkflowChildCancellationCapability(
            "no-in-net-cancellation", False, (), (), "no-propagation", 1
        ),
        reconciliation_capability_identity="runtime-reconciliation",
        execution_protocol_requirement_identity="protocol:1",
        protected_effect_capability_identities=("synthetic-effect",),
        contract_version=1,
    )
    plan = replace(
        execution_plan_closure(),
        child_interface=interface,
        terminal_delivery_requirements=(delivery,),
    )
    plan_identity = WorkflowExecutionPlanIdentityDeriver().execute(
        WorkflowExecutionPlanIdentityDerivationInput(plan)
    )
    return WorkflowChildDefinitionExportClosure(
        owner_identity="synthetic-owner",
        workflow_family_identity="synthetic-child-family",
        source_definition_identity="synthetic-source-definition",
        source_definition_contract_version=1,
        execution_plan_identity=plan_identity,
        execution_plan_sha256=plan_identity.value.rsplit(":", 1)[-1],
        nominal_definition_identity=plan.nominal_definition_identity.value,
        canonical_definition_identity=plan.canonical_definition_identity.value,
        canonical_definition_representation_profile_identity=(
            plan.canonical_definition_representation_profile_identity
        ),
        canonical_definition_sha256=plan.canonical_definition_sha256,
        cpn_execution_profile_identity=plan.cpn_execution_profile_identity,
        initial_marking_constructor_identity=plan.initial_marking_contract_identity,
        interface=interface,
        compiler_implementation_identity=plan.compiler_identity,
        compiler_version_identity=plan.compiler_version,
        exporter_implementation_identity="synthetic-child-exporter",
        exporter_version_identity="0.1",
        source_revision_identity="synthetic-source-revision",
        contract_version=1,
    )


def test_execute__constructs_content_identified_export() -> None:
    """Every complete semantic field contributes before evidence exists."""
    first = WorkflowChildDefinitionExporter().execute(
        WorkflowChildDefinitionExportInput(closure())
    )
    changed = WorkflowChildDefinitionExporter().execute(
        WorkflowChildDefinitionExportInput(
            replace(closure(), source_revision_identity="other-revision")
        )
    )
    assert first.closure == closure()
    assert first.identity != changed.identity


def test_identity__changes_for_one_companion_semantic_field() -> None:
    """Caller text cannot mask a changed companion evidence contract."""
    base = closure().interface.terminal_delivery_requirements[0]
    companion = base.companion_requirements[0]
    changed = replace(
        companion, maximum_payload_bytes=companion.maximum_payload_bytes + 1
    )
    assert changed.identity != companion.identity
    assert (
        replace(base, companion_requirements=(changed,)).identity
        != base.identity
    )


def test_constructor__requires_exactly_one_primary_payload() -> None:
    """A terminal primary is neither optional nor a multi-token collection."""
    base = closure()
    changed_port = replace(
        base.interface.terminal_output_ports[0], minimum_token_count=0
    )
    with pytest.raises(ValueError, match="exactly one payload"):
        replace(
            base,
            interface=replace(
                base.interface, terminal_output_ports=(changed_port,)
            ),
        )


def test_constructor__rejects_unknown_cancellation_terminal() -> None:
    """Supported cancellation cannot name an undeclared terminal class."""
    base = closure()
    capability = WorkflowChildCancellationCapability(
        "cancellation", True, (), ("cancelled",), "propagate", 1
    )
    with pytest.raises(ValueError, match="admitted terminals"):
        replace(
            base,
            interface=replace(
                base.interface, cancellation_capability=capability
            ),
        )


def test_constructor__rejects_fabricated_cancellation_topology() -> None:
    """A provider declaring no in-net cancellation cannot name a port."""
    with pytest.raises(ValueError, match="must not fabricate"):
        WorkflowChildCancellationCapability(
            "invalid", False, ("cancel",), (), "none", 1
        )
