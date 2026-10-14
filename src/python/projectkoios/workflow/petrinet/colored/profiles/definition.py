"""Immutable CPN execution profiles and content identities."""

import json
from dataclasses import dataclass
from hashlib import sha256
from string import hexdigits
from typing import final

from ..firing.transitions import (
    CpnTransitionFirer,
)


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileIdentity:
    """Content-derived identity of one exact CPN execution profile."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("profile identity must be a string")
        prefix = "projectkoios.workflow.cpn-execution-profile:0.1:"
        if not self.value.startswith(prefix):
            raise ValueError("profile identity has the wrong domain")
        digest = self.value.removeprefix(prefix)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError("profile identity must end in lowercase SHA-256")


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfile:
    """Complete exact identities of independently verifiable CPN operations."""

    value_model_identity: str
    expression_grammar_identity: str
    canonical_json_parser_identity: str
    canonical_definition_codec_identity: str
    canonical_control_record_codec_identity: str
    canonical_marking_representation_identity: str
    canonical_binding_representation_identity: str
    canonical_directive_representation_identity: str
    canonical_enablement_result_representation_identity: str
    canonical_selection_result_representation_identity: str
    canonical_firing_result_representation_identity: str
    definition_validator_identity: str
    marking_validator_identity: str
    control_record_type_graph_validator_identity: str
    control_record_schema_validator_identity: str
    expression_structure_validator_identity: str
    expression_bounds_validator_identity: str
    field_projector_identity: str
    control_record_constructor_identity: str
    expression_evaluator_identity: str
    guard_evaluator_identity: str
    value_canonicalizer_identity: str
    value_canonical_decoder_identity: str
    value_expression_canonicalizer_identity: str
    value_expression_decoder_identity: str
    guard_canonicalizer_identity: str
    guard_decoder_identity: str
    expression_variable_collector_identity: str
    guard_expression_collector_identity: str
    guard_variable_collector_identity: str
    value_ordering_policy_identity: str
    token_ordering_policy_identity: str
    external_output_validator_identity: str
    input_arc_validator_identity: str
    output_arc_validator_identity: str
    complete_enabler_identity: str
    enablement_failure_builder_identity: str
    enabled_binding_ordering_identity: str
    binding_selector_identity: str
    transition_firer_identity: str
    token_occurrence_reconstructor_identity: str
    firing_result_identity_deriver_identity: str
    successor_marking_builder_identity: str
    firing_failure_builder_identity: str
    shadow_firer_identity: str
    shadow_firing_replayer_identity: str
    execution_plan_compiler_identity: str
    child_definition_exporter_identity: str
    execution_profile_resolver_identity: str
    semantic_version: str

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileIdentityDeriverIdentity:
    """Identity of execution-profile identity derivation semantics."""

    value: str = "projectkoios.workflow.cpn.profile-identity-deriver:0.1"


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileResolutionIssue:
    """One retained profile component unavailable in this implementation."""

    component_name: str
    retained_identity: str
    supported_identity: str

    def __post_init__(self) -> None:
        for name in (
            "component_name",
            "retained_identity",
            "supported_identity",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileResolutionResult:
    """Component resolution plus the exact operation replay must consume."""

    profile_identity: WorkflowCpnExecutionProfileIdentity
    issues: tuple[WorkflowCpnExecutionProfileResolutionIssue, ...]
    transition_firer: CpnTransitionFirer | None

    def __post_init__(self) -> None:
        if (
            type(self.profile_identity)
            is not WorkflowCpnExecutionProfileIdentity
        ):
            raise TypeError(
                "profile_identity must be WorkflowCpnExecutionProfileIdentity"
            )
        if type(self.issues) is not tuple or any(
            type(item) is not WorkflowCpnExecutionProfileResolutionIssue
            for item in self.issues
        ):
            raise TypeError(
                "issues must contain exact profile-resolution issues"
            )
        names = tuple(item.component_name for item in self.issues)
        if names != tuple(sorted(set(names))):
            raise ValueError(
                "profile-resolution issues must be unique and component-ordered"
            )
        if self.issues:
            if self.transition_firer is not None:
                raise ValueError(
                    "unavailable profiles must not expose an action"
                )
        elif type(self.transition_firer) is not CpnTransitionFirer:
            raise TypeError(
                "available profiles must expose the exact resolved action"
            )

    @property
    def is_available(self) -> bool:
        """Return whether every component and the replay operation resolved."""
        return not self.issues and self.transition_firer is not None


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileIdentityDerivationInput:
    """One exact profile whose content identity is requested."""

    profile: WorkflowCpnExecutionProfile

    def __post_init__(self) -> None:
        if type(self.profile) is not WorkflowCpnExecutionProfile:
            raise TypeError("profile must be WorkflowCpnExecutionProfile")


@final
class WorkflowCpnExecutionProfileIdentityDeriver:
    """Directly derive a profile identity from every component identity."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowCpnExecutionProfileIdentityDeriverIdentity:
        """Return the exact derivation semantics identity."""
        return WorkflowCpnExecutionProfileIdentityDeriverIdentity()

    def execute(
        self,
        derivation_input: WorkflowCpnExecutionProfileIdentityDerivationInput,
    ) -> WorkflowCpnExecutionProfileIdentity:
        """Hash one closed canonical representation of all profile fields."""
        if type(derivation_input) is not (
            WorkflowCpnExecutionProfileIdentityDerivationInput
        ):
            raise TypeError(
                "derivation_input must be "
                "WorkflowCpnExecutionProfileIdentityDerivationInput"
            )
        profile = derivation_input.profile
        state = {
            name: getattr(profile, name)
            for name in profile.__dataclass_fields__
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return WorkflowCpnExecutionProfileIdentity(
            "projectkoios.workflow.cpn-execution-profile:0.1:"
            + sha256(encoded).hexdigest()
        )


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileResolverIdentity:
    """Identity of exact local component-resolution semantics."""

    value: str = "projectkoios.workflow.cpn.execution-profile-resolver:0.1"
