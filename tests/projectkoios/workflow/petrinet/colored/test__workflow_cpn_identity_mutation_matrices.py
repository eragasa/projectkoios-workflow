"""Exhaustive identity and correlation mutation matrices."""

from dataclasses import fields, replace

import pytest

from _child_export_evidence_fixtures import child_export, child_interface
from _plan_fixtures import execution_plan_closure, value_mapping_descriptor
from projectkoios.workflow.petrinet.colored.canonical.definitions import (
    CpnCanonicalDefinition,
)
from projectkoios.workflow.petrinet.colored.children.exports.canonical.identity import (
    WorkflowChildDefinitionExportIdentityDerivationInput,
    WorkflowChildDefinitionExportIdentityDeriver,
)
from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowChildInterface,
)
from projectkoios.workflow.petrinet.colored.definitions import (
    CpnDefinitionIdentity,
)
from projectkoios.workflow.petrinet.colored.plans.identity import (
    WorkflowExecutionPlanIdentityDerivationInput,
    WorkflowExecutionPlanIdentityDeriver,
)
from projectkoios.workflow.petrinet.colored.plans.identities import (
    WorkflowExecutionPlanIdentity,
)
from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileIdentity,
)


def _mutate_plan_field(field_name: str) -> object:
    source = execution_plan_closure()
    mutations: dict[str, object] = {
        "nominal_definition_identity": CpnDefinitionIdentity("other"),
        "canonical_definition": CpnCanonicalDefinition(b"{}"),
        "cpn_execution_profile_identity": WorkflowCpnExecutionProfileIdentity(
            "projectkoios.workflow.cpn-execution-profile:0.1:" + "a" * 64
        ),
        "initial_marking_contract_identity": "other-marking-contract",
        "payload_color_bindings": ("invalid",),
        "transition_routes": (
            replace(source.transition_routes[0], contract_version=2),
        ),
        "child_bindings": ("invalid",),
        "child_interface": child_interface(),
        "terminal_delivery_requirements": ("invalid",),
        "owner_mapping_descriptors": (value_mapping_descriptor(),),
        "compiler_identity": "other-compiler",
        "compiler_version": "other-version",
        "contract_version": 2,
    }
    assert set(mutations) == {
        item.name for item in fields(type(source)) if item.init is not False
    }
    return mutations[field_name]


@pytest.mark.parametrize(
    "field_name",
    tuple(item.name for item in fields(type(execution_plan_closure()))),
)
def test_execution_plan_identity__protects_every_closure_field(
    field_name: str,
) -> None:
    source = execution_plan_closure()
    original = WorkflowExecutionPlanIdentityDeriver().execute(
        WorkflowExecutionPlanIdentityDerivationInput(source)
    )
    try:
        changed = replace(
            source, **{field_name: _mutate_plan_field(field_name)}
        )
    except TypeError, ValueError:
        return
    changed_identity = WorkflowExecutionPlanIdentityDeriver().execute(
        WorkflowExecutionPlanIdentityDerivationInput(changed)
    )
    assert changed_identity != original


def _mutate_interface_field(
    source: WorkflowChildInterface, field_name: str
) -> object:
    mutations: dict[str, object] = {
        "input_ports": (replace(source.input_ports[0], contract_version=2),),
        "terminal_output_ports": (
            replace(source.terminal_output_ports[0], contract_version=2),
        ),
        "admitted_terminal_classification_identities": ("other",),
        "terminal_delivery_requirements": (
            replace(
                source.terminal_delivery_requirements[0],
                mapper_input_ordering_profile_identity="other-ordering",
            ),
        ),
        "cancellation_capability": replace(
            source.cancellation_capability, contract_version=2
        ),
        "reconciliation_capability_identity": "other-reconciliation",
        "execution_protocol_requirement_identity": "other-protocol",
        "protected_effect_capability_identities": (
            "other-effect",
            "synthetic-calculation",
        ),
        "contract_version": 2,
    }
    assert set(mutations) == {
        item.name for item in fields(type(source)) if item.init
    }
    return mutations[field_name]


@pytest.mark.parametrize(
    "field_name",
    tuple(item.name for item in fields(WorkflowChildInterface) if item.init),
)
def test_child_interface_identity__protects_every_semantic_field(
    field_name: str,
) -> None:
    source = child_interface()
    try:
        changed = replace(
            source,
            **{field_name: _mutate_interface_field(source, field_name)},
        )
    except TypeError, ValueError:
        return
    assert changed.identity != source.identity


def _mutate_export_field(field_name: str) -> object:
    source = child_export().closure
    string_fields = {
        "owner_identity",
        "workflow_family_identity",
        "source_definition_identity",
        "nominal_definition_identity",
        "canonical_definition_identity",
        "canonical_definition_representation_profile_identity",
        "initial_marking_constructor_identity",
        "compiler_implementation_identity",
        "compiler_version_identity",
        "exporter_implementation_identity",
        "exporter_version_identity",
        "source_revision_identity",
    }
    if field_name in string_fields:
        return getattr(source, field_name) + ":other"
    if field_name in {
        "source_definition_contract_version",
        "contract_version",
    }:
        return getattr(source, field_name) + 1
    if field_name == "execution_plan_identity":
        return WorkflowExecutionPlanIdentity(
            "projectkoios.workflow.execution-plan:0.1:" + "a" * 64
        )
    if field_name in {
        "execution_plan_sha256",
        "canonical_definition_sha256",
    }:
        return "a" * 64
    if field_name == "cpn_execution_profile_identity":
        return WorkflowCpnExecutionProfileIdentity(
            "projectkoios.workflow.cpn-execution-profile:0.1:" + "a" * 64
        )
    if field_name == "interface":
        return replace(child_interface(), contract_version=2)
    raise AssertionError(field_name)


@pytest.mark.parametrize(
    "field_name",
    tuple(item.name for item in fields(type(child_export().closure))),
)
def test_child_export_identity__protects_every_closure_field(
    field_name: str,
) -> None:
    source = child_export().closure
    original = WorkflowChildDefinitionExportIdentityDeriver().execute(
        WorkflowChildDefinitionExportIdentityDerivationInput(source)
    )
    try:
        changed = replace(
            source, **{field_name: _mutate_export_field(field_name)}
        )
    except TypeError, ValueError:
        return
    changed_identity = WorkflowChildDefinitionExportIdentityDeriver().execute(
        WorkflowChildDefinitionExportIdentityDerivationInput(changed)
    )
    assert changed_identity != original
