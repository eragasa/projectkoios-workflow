"""Verification of bounded experimental pure-action plan closure."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest
from projectkoios.workflow.actions import (
    ExperimentalWorkflowAsciiOutputMappingDescriptor,
    ExperimentalWorkflowSelectedBindingEncoder,
    ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionExecutionBindings,
    ExperimentalWorkflowPureActionExecutionPlan,
    ExperimentalWorkflowPureActionExecutionPlanIdentity,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetValueKind,
)
from projectkoios.workflow_sdk import WORKFLOW_SDK_VERSION
from projectkoios.workflow_sdk.firing import (
    WorkflowFirerDescriptor,
    WorkflowFiringBounds,
    WorkflowTransitionFirerBinding,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowDefinitionIdentity,
    WorkflowFirerIdentity,
    WorkflowFirerImplementationIdentity,
    WorkflowIntegrationIdentity,
    WorkflowPayloadCodecIdentity,
    WorkflowPayloadOwnerIdentity,
    WorkflowPayloadRepresentationIdentity,
    WorkflowPayloadSchemaIdentity,
    WorkflowPayloadTypeIdentity,
    WorkflowTransitionIdentity,
)
from projectkoios.workflow_sdk.integration import WorkflowIntegrationManifest
from projectkoios.workflow_sdk.payloads import WorkflowPayloadContract


def _contract(role: str, maximum: int) -> WorkflowPayloadContract:
    return WorkflowPayloadContract(
        role=role,
        owner_identity=WorkflowPayloadOwnerIdentity("fixture.owner"),
        payload_type_identity=WorkflowPayloadTypeIdentity(f"fixture.{role}"),
        schema_identity=WorkflowPayloadSchemaIdentity(f"fixture.{role}:1"),
        codec_identity=WorkflowPayloadCodecIdentity(f"fixture.{role}-json:1"),
        representation_identity=WorkflowPayloadRepresentationIdentity(
            "canonical-ascii:1"
            if role == "artifact_set_identity"
            else "canonical-json:1"
        ),
        media_type=f"application/vnd.fixture.{role}.v1+json",
        maximum_byte_length=maximum,
    )


def _descriptor(
    *,
    implementation: str = "fixture.firer:1",
) -> WorkflowFirerDescriptor:
    return WorkflowFirerDescriptor(
        identity=WorkflowFirerIdentity("fixture.firer"),
        implementation_identity=WorkflowFirerImplementationIdentity(
            implementation
        ),
        input_contracts=(_contract("projection_request", 128),),
        output_contracts=(_contract("artifact_set_identity", 256),),
        evidence_contracts=(_contract("artifact_set", 1024),),
        bounds=WorkflowFiringBounds(
            maximum_input_count=1,
            maximum_output_count=1,
            maximum_evidence_count=1,
            maximum_input_bytes=128,
            maximum_output_bytes=256,
            maximum_total_bytes=1280,
            maximum_reason_count=1,
        ),
    )


def _mapping(
    *,
    mapping_version: str = "fixture.mapping:1",
    descriptor: WorkflowFirerDescriptor | None = None,
) -> ExperimentalWorkflowAsciiOutputMappingDescriptor:
    firer_descriptor = descriptor or _descriptor()
    transition_binding = WorkflowTransitionFirerBinding(
        definition_identity=WorkflowDefinitionIdentity("fixture.definition"),
        transition_identity=WorkflowTransitionIdentity("fixture.transition"),
        firer_identity=firer_descriptor.identity,
        input_roles=("projection_request",),
        output_roles=("artifact_set_identity",),
        binding_version="fixture.binding:1",
    )
    return ExperimentalWorkflowAsciiOutputMappingDescriptor(
        transition_binding=transition_binding,
        firer_descriptor=firer_descriptor,
        output_role="artifact_set_identity",
        external_variable_identity=ColoredPetriNetBindingVariableIdentity(
            "artifact_set_identity"
        ),
        external_value_kind=ColoredPetriNetValueKind.STRING,
        mapping_version=mapping_version,
    )


def _profile() -> (
    ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity
):
    return ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity(
        ExperimentalWorkflowSelectedBindingEncoder().profile_identity
    )


def _plan(
    *,
    mapping: ExperimentalWorkflowAsciiOutputMappingDescriptor | None = None,
) -> ExperimentalWorkflowPureActionExecutionPlan:
    return ExperimentalWorkflowPureActionExecutionPlan(
        selected_binding_profile_identity=_profile(),
        output_mapping_descriptor=mapping or _mapping(),
    )


def _manifest(
    *descriptors: WorkflowFirerDescriptor,
    distribution_sha256: str = "a" * 64,
) -> WorkflowIntegrationManifest:
    return WorkflowIntegrationManifest(
        integration_identity=WorkflowIntegrationIdentity("fixture.integration"),
        package_name="fixture-integration",
        package_version="1.0.0",
        distribution_sha256=distribution_sha256,
        sdk_contract_version=WORKFLOW_SDK_VERSION,
        firer_descriptors=tuple(
            sorted(descriptors, key=lambda item: item.identity.value)
        ),
    )


def test_plan_closes_profile_and_output_mapping_deterministically() -> None:
    first = _plan()
    replay = _plan()
    changed = _plan(mapping=_mapping(mapping_version="fixture.mapping:2"))

    assert first == replay
    assert first.identity == replay.identity
    assert first.identity != changed.identity
    assert first.selected_binding_profile_identity == _profile()
    assert first.output_mapping_descriptor == _mapping()
    assert first.output_mapping_identity == _mapping().identity


def test_plan_identity_changes_with_profile_and_rejects_forged_mapping() -> (
    None
):
    mapping = _mapping()
    current = _plan(mapping=mapping)
    retained_other_profile = ExperimentalWorkflowPureActionExecutionPlan(
        selected_binding_profile_identity=(
            ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity(
                "fixture.retained-profile:1"
            )
        ),
        output_mapping_descriptor=mapping,
    )

    assert current.identity != retained_other_profile.identity
    assert retained_other_profile.selected_binding_profile_identity.value == (
        "fixture.retained-profile:1"
    )

    object.__setattr__(
        mapping,
        "identity",
        replace(mapping.identity, value="0" * 64),
    )
    with pytest.raises(ValueError, match="mapping differs"):
        _plan(mapping=mapping)


def test_bindings_link_exact_plan_firer_to_manifest() -> None:
    plan = _plan()
    manifest = _manifest(plan.output_mapping_descriptor.firer_descriptor)

    first = ExperimentalWorkflowPureActionExecutionBindings(
        execution_plan=plan,
        integration_manifest=manifest,
    )
    replay = ExperimentalWorkflowPureActionExecutionBindings(
        execution_plan=plan,
        integration_manifest=manifest,
    )
    changed_manifest = _manifest(
        plan.output_mapping_descriptor.firer_descriptor,
        distribution_sha256="b" * 64,
    )
    changed = ExperimentalWorkflowPureActionExecutionBindings(
        execution_plan=plan,
        integration_manifest=changed_manifest,
    )
    retained_profile_plan = ExperimentalWorkflowPureActionExecutionPlan(
        selected_binding_profile_identity=(
            ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity(
                "fixture.retained-profile:1"
            )
        ),
        output_mapping_descriptor=plan.output_mapping_descriptor,
    )
    retained_profile_bindings = ExperimentalWorkflowPureActionExecutionBindings(
        execution_plan=retained_profile_plan,
        integration_manifest=manifest,
    )

    assert first == replay
    assert first.identity == replay.identity
    assert first.identity != changed.identity
    assert first.identity != retained_profile_bindings.identity
    assert retained_profile_bindings.execution_plan == retained_profile_plan
    assert first.output_mapping_identity == plan.output_mapping_identity


def test_bindings_reject_missing_or_changed_plan_firer() -> None:
    plan = _plan()
    missing = _manifest()
    changed = _manifest(_descriptor(implementation="fixture.firer:2"))

    with pytest.raises(ValueError, match="omits the plan firer"):
        ExperimentalWorkflowPureActionExecutionBindings(
            execution_plan=plan,
            integration_manifest=missing,
        )
    with pytest.raises(ValueError, match="firer differs from the plan"):
        ExperimentalWorkflowPureActionExecutionBindings(
            execution_plan=plan,
            integration_manifest=changed,
        )


def test_records_are_frozen_and_revalidate_nested_content() -> None:
    plan = _plan()
    manifest = _manifest(plan.output_mapping_descriptor.firer_descriptor)

    with pytest.raises(FrozenInstanceError):
        plan.identity = ExperimentalWorkflowPureActionExecutionPlanIdentity(
            "0" * 64
        )  # type: ignore[misc]

    object.__setattr__(
        plan,
        "identity",
        ExperimentalWorkflowPureActionExecutionPlanIdentity("0" * 64),
    )
    with pytest.raises(ValueError, match="plan differs"):
        ExperimentalWorkflowPureActionExecutionBindings(
            execution_plan=plan,
            integration_manifest=manifest,
        )
