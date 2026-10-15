"""Experimental canonical CPN closure for one pure-action firing plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from string import hexdigits
from typing import final

from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetDefinition,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetDefinitionValidator,
)

from .pure_action_cpn_representation import (
    _DEFINITION_PROFILE,
    ExperimentalWorkflowCpnDefinitionEncoder,
    ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity,
    _inspect_definition_representation,
)
from .pure_action_inputs import (
    ExperimentalWorkflowPureActionInputPlan,
    ExperimentalWorkflowPureActionInputPlanIdentity,
)

_PLAN_DOMAIN = "projectkoios.workflow.experimental-pure-action-cpn-plan:0"
_PROFILE_DOMAIN = "projectkoios.workflow.experimental-cpn-execution-profile:0"
_MAX_TEXT_BYTES = 512


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowCpnExecutionProfileIdentity:
    """Content identity of one bounded v0 CPN execution profile."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "CPN execution profile identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowCpnExecutionProfile:
    """Close exact implementation-profile names used by candidate firing."""

    identity: ExperimentalWorkflowCpnExecutionProfileIdentity = field(
        init=False
    )
    value_model_identity: str
    expression_grammar_identity: str
    definition_validator_identity: str
    marking_validator_identity: str
    expression_evaluator_identity: str
    transition_enabler_identity: str
    ordering_policy_identity: str
    binding_selector_identity: str
    external_output_validator_identity: str
    transition_firer_identity: str

    def __post_init__(self) -> None:
        values = tuple(
            getattr(self, name)
            for name in (
                "value_model_identity",
                "expression_grammar_identity",
                "definition_validator_identity",
                "marking_validator_identity",
                "expression_evaluator_identity",
                "transition_enabler_identity",
                "ordering_policy_identity",
                "binding_selector_identity",
                "external_output_validator_identity",
                "transition_firer_identity",
            )
        )
        for index, value in enumerate(values):
            _validate_text(value, f"CPN execution profile component {index}")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowCpnExecutionProfileIdentity(
                stable_identity(_PROFILE_DOMAIN, *values)
            ),
        )


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCpnPlanIdentity:
    """Content identity of one bounded v0 CPN-closed plan candidate."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "pure action CPN plan identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCpnPlan:
    """Bind input-plan semantics to exact canonical flat-definition bytes."""

    identity: ExperimentalWorkflowPureActionCpnPlanIdentity = field(init=False)
    definition_sha256: str = field(init=False)
    definition_byte_length: int = field(init=False)
    input_plan_identity: ExperimentalWorkflowPureActionInputPlanIdentity
    definition_identity: ColoredPetriNetDefinitionIdentity
    definition_representation_profile_identity: (
        ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity
    )
    definition_bytes: bytes = field(repr=False)
    execution_profile: ExperimentalWorkflowCpnExecutionProfile

    def __post_init__(self) -> None:
        if type(self.input_plan_identity) is not (
            ExperimentalWorkflowPureActionInputPlanIdentity
        ):
            raise TypeError(
                "input_plan_identity must be "
                "ExperimentalWorkflowPureActionInputPlanIdentity"
            )
        if (
            type(self.definition_identity)
            is not ColoredPetriNetDefinitionIdentity
        ):
            raise TypeError(
                "definition_identity must be ColoredPetriNetDefinitionIdentity"
            )
        if type(self.definition_representation_profile_identity) is not (
            ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity
        ):
            raise TypeError(
                "definition_representation_profile_identity must be "
                "ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity"
            )
        if (
            self.definition_representation_profile_identity.value
            != _DEFINITION_PROFILE
        ):
            raise ValueError("definition representation profile is unsupported")
        if (
            type(self.execution_profile)
            is not ExperimentalWorkflowCpnExecutionProfile
        ):
            raise TypeError(
                "execution_profile must be "
                "ExperimentalWorkflowCpnExecutionProfile"
            )
        profile = ExperimentalWorkflowCpnExecutionProfile(
            value_model_identity=self.execution_profile.value_model_identity,
            expression_grammar_identity=(
                self.execution_profile.expression_grammar_identity
            ),
            definition_validator_identity=(
                self.execution_profile.definition_validator_identity
            ),
            marking_validator_identity=(
                self.execution_profile.marking_validator_identity
            ),
            expression_evaluator_identity=(
                self.execution_profile.expression_evaluator_identity
            ),
            transition_enabler_identity=(
                self.execution_profile.transition_enabler_identity
            ),
            ordering_policy_identity=(
                self.execution_profile.ordering_policy_identity
            ),
            binding_selector_identity=(
                self.execution_profile.binding_selector_identity
            ),
            external_output_validator_identity=(
                self.execution_profile.external_output_validator_identity
            ),
            transition_firer_identity=(
                self.execution_profile.transition_firer_identity
            ),
        )
        if profile != self.execution_profile:
            raise ValueError("execution profile differs after validation")
        byte_length, digest = _inspect_definition_representation(
            self.definition_bytes,
            self.definition_identity,
        )
        object.__setattr__(self, "definition_sha256", digest)
        object.__setattr__(self, "definition_byte_length", byte_length)
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionCpnPlanIdentity(
                stable_identity(
                    _PLAN_DOMAIN,
                    self.input_plan_identity.value,
                    self.definition_identity.value,
                    self.definition_representation_profile_identity.value,
                    byte_length,
                    digest,
                    profile.identity.value,
                )
            ),
        )


@final
class ExperimentalWorkflowPureActionCpnPlanFactory:
    """Construct one CPN-closed plan candidate from exact semantic objects."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionCpnPlanFactory is not subclassable"
        )

    def execute(
        self,
        *,
        input_plan: ExperimentalWorkflowPureActionInputPlan,
        definition: ColoredPetriNetDefinition,
        execution_profile: ExperimentalWorkflowCpnExecutionProfile,
    ) -> ExperimentalWorkflowPureActionCpnPlan:
        """Bind exact definition bytes to one existing input-plan identity."""
        if type(input_plan) is not ExperimentalWorkflowPureActionInputPlan:
            raise TypeError(
                "input_plan must be ExperimentalWorkflowPureActionInputPlan"
            )
        if type(definition) is not ColoredPetriNetDefinition:
            raise TypeError("definition must be ColoredPetriNetDefinition")
        if (
            type(execution_profile)
            is not ExperimentalWorkflowCpnExecutionProfile
        ):
            raise TypeError(
                "execution_profile must be "
                "ExperimentalWorkflowCpnExecutionProfile"
            )
        validation = ColoredPetriNetDefinitionValidator().execute(definition)
        if not validation.is_valid:
            raise ValueError("definition must pass structural validation")
        mapping = input_plan.execution_plan.output_mapping_descriptor
        if (
            definition.identity.value
            != mapping.transition_binding.definition_identity.value
        ):
            raise ValueError("definition identity differs from input plan")
        transitions = tuple(
            item
            for item in definition.transitions
            if item.identity.value
            == mapping.transition_binding.transition_identity.value
        )
        if len(transitions) != 1:
            raise ValueError("definition does not contain the plan transition")
        encoder = ExperimentalWorkflowCpnDefinitionEncoder()
        return ExperimentalWorkflowPureActionCpnPlan(
            input_plan_identity=input_plan.identity,
            definition_identity=definition.identity,
            definition_representation_profile_identity=(
                encoder.profile_identity
            ),
            definition_bytes=encoder.encode(definition),
            execution_profile=execution_profile,
        )


def experimental_shadow_cpn_execution_profile() -> (
    ExperimentalWorkflowCpnExecutionProfile
):
    """Return the installed provenance-bound candidate profile."""
    return ExperimentalWorkflowCpnExecutionProfile(
        value_model_identity="shadow-cpn-value-model:1",
        expression_grammar_identity="shadow-cpn-expression-grammar:1",
        definition_validator_identity="shadow-cpn-definition-validator:1",
        marking_validator_identity="shadow-cpn-marking-validator:1",
        expression_evaluator_identity="shadow-cpn-expression-evaluator:1",
        transition_enabler_identity="shadow-cpn-transition-enabler:1",
        ordering_policy_identity="shadow-cpn-enabled-binding-order:1",
        binding_selector_identity="shadow-cpn-binding-selector:1",
        external_output_validator_identity=(
            "shadow-cpn-external-output-validator:1"
        ),
        transition_firer_identity="shadow-cpn-transition-firer:1",
    )


def _validate_text(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if not value:
        raise ValueError(f"{label} must not be empty")
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{label} must be valid UTF-8") from exc
    if len(encoded) > _MAX_TEXT_BYTES:
        raise ValueError(f"{label} exceeds {_MAX_TEXT_BYTES} bytes")


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
    "ExperimentalWorkflowCpnDefinitionEncoder",
    "ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity",
    "ExperimentalWorkflowCpnExecutionProfile",
    "ExperimentalWorkflowCpnExecutionProfileIdentity",
    "ExperimentalWorkflowPureActionCpnPlan",
    "ExperimentalWorkflowPureActionCpnPlanFactory",
    "ExperimentalWorkflowPureActionCpnPlanIdentity",
    "experimental_shadow_cpn_execution_profile",
]
