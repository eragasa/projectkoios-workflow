"""Direct tests for complete profile/plan/export identity closure."""

from _plan_fixtures import execution_plan_closure, value_mapping_descriptor

from dataclasses import fields, replace

import pytest

from projectkoios.workflow.petrinet.colored.children.exports.definition import (
    WorkflowChildDefinitionExportClosure,
)
from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowChildCancellationCapability,
    WorkflowChildInterface,
    WorkflowChildPortDefinition,
    WorkflowChildPortDirection,
    WorkflowChildPortTrafficKind,
    WorkflowTerminalDeliveryRequirement,
)
from projectkoios.workflow.petrinet.colored.closure.validation import (
    WorkflowCpnClosureCorrelationInput,
    WorkflowCpnClosureCorrelationValidator,
)
from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanIdentityDerivationInput,
    WorkflowExecutionPlanIdentityDeriver,
)
from projectkoios.workflow.petrinet.colored.profiles.defaults import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
)
from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileIdentityDerivationInput,
    WorkflowCpnExecutionProfileIdentityDeriver,
)


@pytest.mark.parametrize(
    "field_name",
    tuple(
        item.name
        for item in fields(
            WorkflowCpnExecutionProfileBuilder().execute(
                WorkflowCpnExecutionProfileBuildingRequest()
            )
        )
    ),
)
def test_identity__changes_for_every_component_substitution(
    field_name: str,
) -> None:
    """Replacing any one profile component changes the profile identity."""
    profile = WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )
    deriver = WorkflowCpnExecutionProfileIdentityDeriver()
    first = deriver.execute(
        WorkflowCpnExecutionProfileIdentityDerivationInput(profile)
    )
    second = deriver.execute(
        WorkflowCpnExecutionProfileIdentityDerivationInput(
            replace(
                profile,
                **{field_name: getattr(profile, field_name) + ":substituted"},
            )
        )
    )
    assert first != second


def test_plan_identity__changes_for_mapping_descriptor_mutation() -> None:
    """Owner mapping descriptors are semantic plan-identity input."""
    first_plan = execution_plan_closure(
        mapping=value_mapping_descriptor(adapter_identity="mapping-a")
    )
    second_plan = execution_plan_closure(
        mapping=value_mapping_descriptor(adapter_identity="mapping-b")
    )
    deriver = WorkflowExecutionPlanIdentityDeriver()
    first = deriver.execute(
        WorkflowExecutionPlanIdentityDerivationInput(first_plan)
    )
    second = deriver.execute(
        WorkflowExecutionPlanIdentityDerivationInput(second_plan)
    )
    assert first != second


def test_correlation__accepts_exact_redundant_closure() -> None:
    """Profile, plan, export, and definition correlations close exactly."""
    profile = WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )
    profile_identity = WorkflowCpnExecutionProfileIdentityDeriver().execute(
        WorkflowCpnExecutionProfileIdentityDerivationInput(profile)
    )
    plan = execution_plan_closure()
    terminal_port = WorkflowChildPortDefinition(
        "terminal-port",
        WorkflowChildPortDirection.OUTPUT,
        "terminal-place",
        "terminal-color",
        "payload-schema",
        "payload-codec",
        None,
        1,
        1,
        (),
        WorkflowChildPortTrafficKind.TERMINAL,
        1,
    )
    delivery_requirement = WorkflowTerminalDeliveryRequirement(
        "success",
        terminal_port.identity,
        "payload-schema",
        "payload-codec",
        (),
        0,
        "primary-then-companions",
        "correlation-validator",
        "output-mapper",
        1,
    )
    interface = WorkflowChildInterface(
        input_ports=(),
        terminal_output_ports=(terminal_port,),
        admitted_terminal_classification_identities=("success",),
        terminal_delivery_requirements=(delivery_requirement,),
        cancellation_capability=WorkflowChildCancellationCapability(
            "no-cancellation", False, (), (), "no-propagation", 1
        ),
        reconciliation_capability_identity="reconciliation",
        execution_protocol_requirement_identity="protocol:1",
        protected_effect_capability_identities=("authority",),
        contract_version=1,
    )
    plan = replace(
        plan,
        child_interface=interface,
        terminal_delivery_requirements=(delivery_requirement,),
    )
    plan_identity = WorkflowExecutionPlanIdentityDeriver().execute(
        WorkflowExecutionPlanIdentityDerivationInput(plan)
    )
    export = WorkflowChildDefinitionExportClosure(
        owner_identity="owner",
        workflow_family_identity="family",
        source_definition_identity="source-definition",
        source_definition_contract_version=1,
        execution_plan_identity=plan_identity,
        execution_plan_sha256=plan_identity.value.rsplit(":", 1)[-1],
        nominal_definition_identity=plan.nominal_definition_identity.value,
        canonical_definition_identity=plan.canonical_definition_identity.value,
        canonical_definition_representation_profile_identity=(
            plan.canonical_definition_representation_profile_identity
        ),
        canonical_definition_sha256=plan.canonical_definition_sha256,
        cpn_execution_profile_identity=profile_identity,
        initial_marking_constructor_identity=plan.initial_marking_contract_identity,
        interface=interface,
        compiler_implementation_identity="compiler",
        compiler_version_identity="1",
        exporter_implementation_identity="exporter",
        exporter_version_identity="1",
        source_revision_identity="revision",
        contract_version=1,
    )
    result = WorkflowCpnClosureCorrelationValidator().execute(
        WorkflowCpnClosureCorrelationInput(
            profile, profile_identity, plan, plan_identity, export
        )
    )
    assert result.is_valid
