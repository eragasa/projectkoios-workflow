"""Models and construction for canonical pure-CPN replay transcripts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits
from typing import final

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowCpnDefinitionDecoder,
    ExperimentalWorkflowCpnDefinitionEncoder,
    ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity,
    ExperimentalWorkflowCpnExecutionProfile,
    ExperimentalWorkflowCpnMarkingDecoder,
    ExperimentalWorkflowCpnMarkingEncoder,
    ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity,
    ExperimentalWorkflowPureActionCpnPlan,
    ExperimentalWorkflowPureActionCpnPlanIdentity,
    ExperimentalWorkflowPureActionInputPlanIdentity,
)
from projectkoios.workflow.compilation._cpn_representation import (
    value_from_state,
    value_state,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetFiringOutcomeKind,
    ColoredPetriNetFiringResult,
    ColoredPetriNetFiringResultIdentity,
    ColoredPetriNetSelectionDirectiveIdentity,
    ColoredPetriNetTransitionFirer,
    ColoredPetriNetTransitionIdentity,
)

_BUNDLE_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-cpn-replay-bundle:0"
)
_MAX_BINDING_ASSIGNMENTS = 65_536


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCpnReplayBundleIdentity:
    """Content identity of one bounded v0 pure-CPN replay transcript."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "CPN replay bundle identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCpnReplayBundle:
    """Retain only the pure CPN state required for deterministic refiring."""

    identity: ExperimentalWorkflowPureActionCpnReplayBundleIdentity = field(
        init=False
    )
    cpn_plan_identity: ExperimentalWorkflowPureActionCpnPlanIdentity
    input_plan_identity: ExperimentalWorkflowPureActionInputPlanIdentity
    execution_profile: ExperimentalWorkflowCpnExecutionProfile
    definition_representation_profile_identity: (
        ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity
    )
    definition_bytes: bytes = field(repr=False)
    predecessor_marking_representation_profile_identity: (
        ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity
    )
    predecessor_marking_bytes: bytes = field(repr=False)
    successor_marking_representation_profile_identity: (
        ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity
    )
    successor_marking_bytes: bytes = field(repr=False)
    transition_identity: ColoredPetriNetTransitionIdentity
    selected_binding: ColoredPetriNetBinding
    directive_identity: ColoredPetriNetSelectionDirectiveIdentity | None
    external_output_binding: ColoredPetriNetBinding
    expected_firing_result_identity: ColoredPetriNetFiringResultIdentity

    def __post_init__(self) -> None:
        if type(self.cpn_plan_identity) is not (
            ExperimentalWorkflowPureActionCpnPlanIdentity
        ):
            raise TypeError(
                "cpn_plan_identity must be "
                "ExperimentalWorkflowPureActionCpnPlanIdentity"
            )
        if type(self.input_plan_identity) is not (
            ExperimentalWorkflowPureActionInputPlanIdentity
        ):
            raise TypeError(
                "input_plan_identity must be "
                "ExperimentalWorkflowPureActionInputPlanIdentity"
            )
        profile = _reconstruct_execution_profile(self.execution_profile)
        definition_decoder = ExperimentalWorkflowCpnDefinitionDecoder()
        marking_decoder = ExperimentalWorkflowCpnMarkingDecoder()
        if (
            type(self.definition_representation_profile_identity)
            is not (
                ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity
            )
            or self.definition_representation_profile_identity
            != definition_decoder.profile_identity
        ):
            raise ValueError("definition representation profile is unsupported")
        for name in (
            "predecessor_marking_representation_profile_identity",
            "successor_marking_representation_profile_identity",
        ):
            value = getattr(self, name)
            if (
                type(value)
                is not (
                    ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity
                )
                or value != marking_decoder.profile_identity
            ):
                raise ValueError(
                    "marking representation profile is unsupported"
                )
        definition = definition_decoder.decode(self.definition_bytes)
        predecessor = marking_decoder.decode(self.predecessor_marking_bytes)
        successor = marking_decoder.decode(self.successor_marking_bytes)
        if (
            predecessor.definition_identity != definition.identity
            or successor.definition_identity != definition.identity
        ):
            raise ValueError(
                "replay markings differ from the replay definition"
            )
        reconstructed_plan = ExperimentalWorkflowPureActionCpnPlan(
            input_plan_identity=self.input_plan_identity,
            definition_identity=definition.identity,
            definition_representation_profile_identity=(
                self.definition_representation_profile_identity
            ),
            definition_bytes=self.definition_bytes,
            execution_profile=profile,
        )
        if reconstructed_plan.identity != self.cpn_plan_identity:
            raise ValueError("CPN plan identity differs from replay state")
        if (
            type(self.transition_identity)
            is not ColoredPetriNetTransitionIdentity
        ):
            raise TypeError(
                "transition_identity must be ColoredPetriNetTransitionIdentity"
            )
        selected = _reconstruct_binding(self.selected_binding)
        external = _reconstruct_binding(self.external_output_binding)
        if (
            selected.transition_identity != self.transition_identity
            or external.transition_identity != self.transition_identity
        ):
            raise ValueError("replay bindings differ from the transition")
        if self.directive_identity is not None and (
            type(self.directive_identity)
            is not ColoredPetriNetSelectionDirectiveIdentity
        ):
            raise TypeError(
                "directive_identity must be "
                "ColoredPetriNetSelectionDirectiveIdentity or None"
            )
        if type(self.expected_firing_result_identity) is not (
            ColoredPetriNetFiringResultIdentity
        ):
            raise TypeError(
                "expected_firing_result_identity must be "
                "ColoredPetriNetFiringResultIdentity"
            )
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionCpnReplayBundleIdentity(
                stable_identity(
                    _BUNDLE_DOMAIN,
                    self.cpn_plan_identity.value,
                    self.input_plan_identity.value,
                    profile.identity.value,
                    self.definition_representation_profile_identity.value,
                    len(self.definition_bytes),
                    sha256(self.definition_bytes).hexdigest(),
                    self.predecessor_marking_representation_profile_identity.value,
                    len(self.predecessor_marking_bytes),
                    sha256(self.predecessor_marking_bytes).hexdigest(),
                    self.successor_marking_representation_profile_identity.value,
                    len(self.successor_marking_bytes),
                    sha256(self.successor_marking_bytes).hexdigest(),
                    self.transition_identity.value,
                    sha256(_binding_bytes(selected)).hexdigest(),
                    None
                    if self.directive_identity is None
                    else self.directive_identity.value,
                    sha256(_binding_bytes(external)).hexdigest(),
                    self.expected_firing_result_identity.value,
                )
            ),
        )


@final
class ExperimentalWorkflowPureActionCpnReplayBundleFactory:
    """Construct one replay bundle from an exact successful firing candidate."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionCpnReplayBundleFactory "
            "is not subclassable"
        )

    def execute(
        self,
        *,
        cpn_plan: ExperimentalWorkflowPureActionCpnPlan,
        firing_result: ColoredPetriNetFiringResult,
    ) -> ExperimentalWorkflowPureActionCpnReplayBundle:
        """Capture exact pure inputs and expected successful output state."""
        if type(cpn_plan) is not ExperimentalWorkflowPureActionCpnPlan:
            raise TypeError(
                "cpn_plan must be ExperimentalWorkflowPureActionCpnPlan"
            )
        if type(firing_result) is not ColoredPetriNetFiringResult:
            raise TypeError("firing_result must be ColoredPetriNetFiringResult")
        replayed = ColoredPetriNetTransitionFirer().execute(
            firing_result.firing_input
        )
        if replayed != firing_result:
            raise ValueError("firing_result differs from pure refiring")
        if (
            firing_result.outcome
            is not ColoredPetriNetFiringOutcomeKind.SUCCESS
            or firing_result.successor_marking is None
        ):
            raise ValueError("CPN replay bundle requires successful firing")
        firing_input = firing_result.firing_input
        definition_encoder = ExperimentalWorkflowCpnDefinitionEncoder()
        if (
            cpn_plan.definition_representation_profile_identity
            != definition_encoder.profile_identity
            or cpn_plan.definition_bytes
            != definition_encoder.encode(firing_input.definition)
            or cpn_plan.definition_identity != firing_input.definition.identity
        ):
            raise ValueError("CPN plan differs from firing definition")
        marking_encoder = ExperimentalWorkflowCpnMarkingEncoder()
        return ExperimentalWorkflowPureActionCpnReplayBundle(
            cpn_plan_identity=cpn_plan.identity,
            input_plan_identity=cpn_plan.input_plan_identity,
            execution_profile=cpn_plan.execution_profile,
            definition_representation_profile_identity=(
                cpn_plan.definition_representation_profile_identity
            ),
            definition_bytes=cpn_plan.definition_bytes,
            predecessor_marking_representation_profile_identity=(
                marking_encoder.profile_identity
            ),
            predecessor_marking_bytes=marking_encoder.encode(
                firing_input.predecessor_marking
            ),
            successor_marking_representation_profile_identity=(
                marking_encoder.profile_identity
            ),
            successor_marking_bytes=marking_encoder.encode(
                firing_result.successor_marking
            ),
            transition_identity=firing_input.transition_identity,
            selected_binding=firing_input.selected_binding,
            directive_identity=firing_input.directive_identity,
            external_output_binding=firing_input.external_output_binding,
            expected_firing_result_identity=firing_result.identity,
        )


def _binding_bytes(value: ColoredPetriNetBinding) -> bytes:
    binding = _reconstruct_binding(value)
    state = {
        "assignments": [
            {
                "value": value_state(item.value),
                "variable_identity": item.variable_identity.value,
            }
            for item in binding.assignments
        ],
        "transition_identity": binding.transition_identity.value,
    }
    return json.dumps(
        state,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _reconstruct_binding(
    value: ColoredPetriNetBinding,
) -> ColoredPetriNetBinding:
    if type(value) is not ColoredPetriNetBinding:
        raise TypeError("binding must be ColoredPetriNetBinding")
    if len(value.assignments) > _MAX_BINDING_ASSIGNMENTS:
        raise ValueError("binding assignments exceed their count bound")
    reconstructed = ColoredPetriNetBinding(
        transition_identity=ColoredPetriNetTransitionIdentity(
            value.transition_identity.value
        ),
        assignments=tuple(
            ColoredPetriNetBindingAssignment(
                variable_identity=ColoredPetriNetBindingVariableIdentity(
                    item.variable_identity.value
                ),
                value=value_from_state(value_state(item.value)),
            )
            for item in value.assignments
        ),
    )
    if reconstructed != value:
        raise ValueError("binding differs after reconstruction")
    return reconstructed


def _reconstruct_execution_profile(
    value: ExperimentalWorkflowCpnExecutionProfile,
) -> ExperimentalWorkflowCpnExecutionProfile:
    if type(value) is not ExperimentalWorkflowCpnExecutionProfile:
        raise TypeError(
            "execution_profile must be ExperimentalWorkflowCpnExecutionProfile"
        )
    reconstructed = ExperimentalWorkflowCpnExecutionProfile(
        value_model_identity=value.value_model_identity,
        expression_grammar_identity=value.expression_grammar_identity,
        definition_validator_identity=value.definition_validator_identity,
        marking_validator_identity=value.marking_validator_identity,
        expression_evaluator_identity=value.expression_evaluator_identity,
        transition_enabler_identity=value.transition_enabler_identity,
        ordering_policy_identity=value.ordering_policy_identity,
        binding_selector_identity=value.binding_selector_identity,
        external_output_validator_identity=(
            value.external_output_validator_identity
        ),
        transition_firer_identity=value.transition_firer_identity,
    )
    if reconstructed != value:
        raise ValueError("execution profile differs after reconstruction")
    return reconstructed


def _validate_sha256(value: object, label: str) -> None:
    if (
        type(value) is not str
        or len(value) != 64
        or value != value.lower()
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


__all__ = [
    "ExperimentalWorkflowPureActionCpnReplayBundle",
    "ExperimentalWorkflowPureActionCpnReplayBundleFactory",
    "ExperimentalWorkflowPureActionCpnReplayBundleIdentity",
]
