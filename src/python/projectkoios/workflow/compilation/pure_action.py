"""Experimental plan and deployment closure for one pure external action."""

from __future__ import annotations

from dataclasses import dataclass, field
from string import hexdigits

from projectkoios.workflow.actions import (
    ExperimentalWorkflowActionResultMappingIdentity,
    ExperimentalWorkflowAsciiOutputMappingDescriptor,
    ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow_sdk.integration import WorkflowIntegrationManifest
from projectkoios.workflow_sdk.serialization import (
    WorkflowIntegrationManifestJsonCodec,
)

_PLAN_IDENTITY_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-execution-plan:1"
)
_BINDINGS_IDENTITY_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-execution-bindings:1"
)


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionExecutionPlanIdentity:
    """Content identity of one bounded experimental pure-action plan."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "pure action execution plan identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionExecutionBindingsIdentity:
    """Content identity of one bounded experimental deployment linking."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "pure action execution bindings identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionExecutionPlan:
    """Close the available semantics for one experimental pure action.

    This record is an embeddable candidate for the complete execution plan. It
    deliberately does not claim definition, marking, route, child, compiler, or
    complete CPN execution-profile closure.
    """

    identity: ExperimentalWorkflowPureActionExecutionPlanIdentity = field(
        init=False
    )
    selected_binding_profile_identity: (
        ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity
    )
    output_mapping_descriptor: ExperimentalWorkflowAsciiOutputMappingDescriptor

    def __post_init__(self) -> None:
        if type(self.selected_binding_profile_identity) is not (
            ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity
        ):
            raise TypeError(
                "selected_binding_profile_identity must be "
                "ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity"
            )
        if type(self.output_mapping_descriptor) is not (
            ExperimentalWorkflowAsciiOutputMappingDescriptor
        ):
            raise TypeError(
                "output_mapping_descriptor must be "
                "ExperimentalWorkflowAsciiOutputMappingDescriptor"
            )
        mapping = self.output_mapping_descriptor
        validated_mapping = ExperimentalWorkflowAsciiOutputMappingDescriptor(
            transition_binding=mapping.transition_binding,
            firer_descriptor=mapping.firer_descriptor,
            output_role=mapping.output_role,
            external_variable_identity=mapping.external_variable_identity,
            external_value_kind=mapping.external_value_kind,
            mapping_version=mapping.mapping_version,
            decoder_profile_identity=mapping.decoder_profile_identity,
        )
        if validated_mapping != mapping:
            raise ValueError("output mapping differs after validation")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionExecutionPlanIdentity(
                stable_identity(
                    _PLAN_IDENTITY_DOMAIN,
                    self.selected_binding_profile_identity.value,
                    mapping.identity.value,
                )
            ),
        )

    @property
    def output_mapping_identity(
        self,
    ) -> ExperimentalWorkflowActionResultMappingIdentity:
        """Return the exact plan-selected output-mapping identity."""
        return self.output_mapping_descriptor.identity


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionExecutionBindings:
    """Link one exact pure-action plan candidate to an SDK manifest."""

    identity: ExperimentalWorkflowPureActionExecutionBindingsIdentity = field(
        init=False
    )
    execution_plan: ExperimentalWorkflowPureActionExecutionPlan
    integration_manifest: WorkflowIntegrationManifest

    def __post_init__(self) -> None:
        if type(self.execution_plan) is not (
            ExperimentalWorkflowPureActionExecutionPlan
        ):
            raise TypeError(
                "execution_plan must be "
                "ExperimentalWorkflowPureActionExecutionPlan"
            )
        if type(self.integration_manifest) is not WorkflowIntegrationManifest:
            raise TypeError(
                "integration_manifest must be WorkflowIntegrationManifest"
            )
        plan = ExperimentalWorkflowPureActionExecutionPlan(
            selected_binding_profile_identity=(
                self.execution_plan.selected_binding_profile_identity
            ),
            output_mapping_descriptor=(
                self.execution_plan.output_mapping_descriptor
            ),
        )
        if plan != self.execution_plan:
            raise ValueError("execution plan differs after validation")
        codec = WorkflowIntegrationManifestJsonCodec()
        manifest = codec.decode(codec.encode(self.integration_manifest))
        if manifest != self.integration_manifest:
            raise ValueError("integration manifest differs after validation")

        required = plan.output_mapping_descriptor.firer_descriptor
        matches = tuple(
            descriptor
            for descriptor in manifest.firer_descriptors
            if descriptor.identity == required.identity
        )
        if not matches:
            raise ValueError("integration manifest omits the plan firer")
        if matches != (required,):
            raise ValueError("integration manifest firer differs from the plan")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionExecutionBindingsIdentity(
                stable_identity(
                    _BINDINGS_IDENTITY_DOMAIN,
                    plan.identity.value,
                    manifest.identity.value,
                )
            ),
        )

    @property
    def output_mapping_identity(
        self,
    ) -> ExperimentalWorkflowActionResultMappingIdentity:
        """Return the exact plan-selected mapping verified at linking."""
        return self.execution_plan.output_mapping_identity


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


__all__ = [
    "ExperimentalWorkflowPureActionExecutionBindings",
    "ExperimentalWorkflowPureActionExecutionBindingsIdentity",
    "ExperimentalWorkflowPureActionExecutionPlan",
    "ExperimentalWorkflowPureActionExecutionPlanIdentity",
]
