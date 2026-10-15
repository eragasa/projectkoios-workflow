"""Canonical serialization for pure-CPN replay transcripts."""

from __future__ import annotations

import base64
import binascii
import json
from typing import final

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity,
    ExperimentalWorkflowCpnExecutionProfile,
    ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity,
    ExperimentalWorkflowPureActionCpnPlanIdentity,
    ExperimentalWorkflowPureActionInputPlanIdentity,
)
from projectkoios.workflow.compilation._cpn_representation import (
    closed_array,
    closed_object,
    exact_text,
    value_from_state,
    value_state,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetFiringResultIdentity,
    ColoredPetriNetSelectionDirectiveIdentity,
    ColoredPetriNetTransitionIdentity,
)

from .pure_action_cpn_replay_bundle import (
    ExperimentalWorkflowPureActionCpnReplayBundle,
    ExperimentalWorkflowPureActionCpnReplayBundleIdentity,
    _reconstruct_binding,
    _reconstruct_execution_profile,
)

_BUNDLE_SCHEMA = (
    "projectkoios.workflow.experimental-pure-action-cpn-replay-json:0"
)
_MAX_BUNDLE_BYTES = 64 * 1024 * 1024
_MAX_BINDING_ASSIGNMENTS = 65_536


@final
class ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec:
    """Encode and decode the exact canonical v0 pure-CPN replay transcript."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec "
            "is not subclassable"
        )

    def encode(
        self, value: ExperimentalWorkflowPureActionCpnReplayBundle
    ) -> bytes:
        """Return bounded canonical bytes for one reconstructed bundle."""
        bundle = _reconstruct_bundle(value)
        payload = json.dumps(
            {
                "bundle": {
                    "bundle_identity": bundle.identity.value,
                    "cpn_plan_identity": bundle.cpn_plan_identity.value,
                    "definition_bytes_base64": _base64_encode(
                        bundle.definition_bytes
                    ),
                    "definition_representation_profile_identity": (
                        bundle.definition_representation_profile_identity.value
                    ),
                    "directive_identity": (
                        None
                        if bundle.directive_identity is None
                        else bundle.directive_identity.value
                    ),
                    "execution_profile": _execution_profile_state(
                        bundle.execution_profile
                    ),
                    "expected_firing_result_identity": (
                        bundle.expected_firing_result_identity.value
                    ),
                    "external_output_binding": _binding_state(
                        bundle.external_output_binding
                    ),
                    "input_plan_identity": bundle.input_plan_identity.value,
                    "predecessor_marking_bytes_base64": _base64_encode(
                        bundle.predecessor_marking_bytes
                    ),
                    "predecessor_marking_representation_profile_identity": (
                        bundle.predecessor_marking_representation_profile_identity.value
                    ),
                    "selected_binding": _binding_state(bundle.selected_binding),
                    "successor_marking_bytes_base64": _base64_encode(
                        bundle.successor_marking_bytes
                    ),
                    "successor_marking_representation_profile_identity": (
                        bundle.successor_marking_representation_profile_identity.value
                    ),
                    "transition_identity": bundle.transition_identity.value,
                },
                "schema": _BUNDLE_SCHEMA,
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(payload) > _MAX_BUNDLE_BYTES:
            raise ValueError("CPN replay bundle exceeds its byte bound")
        return payload

    def decode(
        self, value: bytes
    ) -> ExperimentalWorkflowPureActionCpnReplayBundle:
        """Decode only the exact bounded canonical v0 transcript schema."""
        if type(value) is not bytes:
            raise TypeError("CPN replay bundle must be bytes")
        if not value or len(value) > _MAX_BUNDLE_BYTES:
            raise ValueError("CPN replay bundle must be nonempty and bounded")
        try:
            parsed = json.loads(value.decode("utf-8"))
            canonical = json.dumps(
                parsed,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        except (
            UnicodeDecodeError,
            UnicodeEncodeError,
            json.JSONDecodeError,
            ValueError,
            RecursionError,
        ) as exc:
            raise ValueError(
                "CPN replay bundle must be canonical UTF-8 JSON"
            ) from exc
        if canonical != value:
            raise ValueError("CPN replay bundle must use canonical JSON")
        root = closed_object(parsed, {"bundle", "schema"})
        if root["schema"] != _BUNDLE_SCHEMA:
            raise ValueError("CPN replay bundle schema is unsupported")
        bundle = closed_object(
            root["bundle"],
            {
                "bundle_identity",
                "cpn_plan_identity",
                "definition_bytes_base64",
                "definition_representation_profile_identity",
                "directive_identity",
                "execution_profile",
                "expected_firing_result_identity",
                "external_output_binding",
                "input_plan_identity",
                "predecessor_marking_bytes_base64",
                "predecessor_marking_representation_profile_identity",
                "selected_binding",
                "successor_marking_bytes_base64",
                "successor_marking_representation_profile_identity",
                "transition_identity",
            },
        )
        try:
            directive_value = bundle["directive_identity"]
            decoded = ExperimentalWorkflowPureActionCpnReplayBundle(
                cpn_plan_identity=ExperimentalWorkflowPureActionCpnPlanIdentity(
                    exact_text(bundle["cpn_plan_identity"])
                ),
                input_plan_identity=ExperimentalWorkflowPureActionInputPlanIdentity(
                    exact_text(bundle["input_plan_identity"])
                ),
                execution_profile=_execution_profile_from_state(
                    bundle["execution_profile"]
                ),
                definition_representation_profile_identity=(
                    ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity(
                        exact_text(
                            bundle["definition_representation_profile_identity"]
                        )
                    )
                ),
                definition_bytes=_base64_decode(
                    bundle["definition_bytes_base64"]
                ),
                predecessor_marking_representation_profile_identity=(
                    ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity(
                        exact_text(
                            bundle[
                                "predecessor_marking_representation_profile_identity"
                            ]
                        )
                    )
                ),
                predecessor_marking_bytes=_base64_decode(
                    bundle["predecessor_marking_bytes_base64"]
                ),
                successor_marking_representation_profile_identity=(
                    ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity(
                        exact_text(
                            bundle[
                                "successor_marking_representation_profile_identity"
                            ]
                        )
                    )
                ),
                successor_marking_bytes=_base64_decode(
                    bundle["successor_marking_bytes_base64"]
                ),
                transition_identity=ColoredPetriNetTransitionIdentity(
                    exact_text(bundle["transition_identity"])
                ),
                selected_binding=_binding_from_state(
                    bundle["selected_binding"]
                ),
                directive_identity=(
                    None
                    if directive_value is None
                    else ColoredPetriNetSelectionDirectiveIdentity(
                        exact_text(directive_value)
                    )
                ),
                external_output_binding=_binding_from_state(
                    bundle["external_output_binding"]
                ),
                expected_firing_result_identity=ColoredPetriNetFiringResultIdentity(
                    exact_text(bundle["expected_firing_result_identity"])
                ),
            )
            retained_identity = (
                ExperimentalWorkflowPureActionCpnReplayBundleIdentity(
                    exact_text(bundle["bundle_identity"])
                )
            )
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError(
                "CPN replay bundle contains invalid state"
            ) from exc
        if decoded.identity != retained_identity:
            raise ValueError(
                "CPN replay bundle identity differs from its state"
            )
        if self.encode(decoded) != value:
            raise ValueError("CPN replay bundle differs after reconstruction")
        return decoded


def _binding_state(value: ColoredPetriNetBinding) -> dict[str, object]:
    binding = _reconstruct_binding(value)
    return {
        "assignments": [
            {
                "value": value_state(item.value),
                "variable_identity": item.variable_identity.value,
            }
            for item in binding.assignments
        ],
        "transition_identity": binding.transition_identity.value,
    }


def _binding_from_state(value: object) -> ColoredPetriNetBinding:
    state = closed_object(value, {"assignments", "transition_identity"})
    assignments_value = closed_array(state["assignments"])
    if len(assignments_value) > _MAX_BINDING_ASSIGNMENTS:
        raise ValueError("binding assignments exceed their count bound")
    assignments = []
    for item in assignments_value:
        assignment = closed_object(item, {"value", "variable_identity"})
        assignments.append(
            ColoredPetriNetBindingAssignment(
                variable_identity=ColoredPetriNetBindingVariableIdentity(
                    exact_text(assignment["variable_identity"])
                ),
                value=value_from_state(assignment["value"]),
            )
        )
    return ColoredPetriNetBinding(
        transition_identity=ColoredPetriNetTransitionIdentity(
            exact_text(state["transition_identity"])
        ),
        assignments=tuple(assignments),
    )


def _execution_profile_state(
    value: ExperimentalWorkflowCpnExecutionProfile,
) -> dict[str, object]:
    profile = _reconstruct_execution_profile(value)
    return {
        "binding_selector_identity": profile.binding_selector_identity,
        "definition_validator_identity": profile.definition_validator_identity,
        "expression_evaluator_identity": profile.expression_evaluator_identity,
        "expression_grammar_identity": profile.expression_grammar_identity,
        "external_output_validator_identity": (
            profile.external_output_validator_identity
        ),
        "identity": profile.identity.value,
        "marking_validator_identity": profile.marking_validator_identity,
        "ordering_policy_identity": profile.ordering_policy_identity,
        "transition_enabler_identity": profile.transition_enabler_identity,
        "transition_firer_identity": profile.transition_firer_identity,
        "value_model_identity": profile.value_model_identity,
    }


def _execution_profile_from_state(
    value: object,
) -> ExperimentalWorkflowCpnExecutionProfile:
    state = closed_object(
        value,
        {
            "binding_selector_identity",
            "definition_validator_identity",
            "expression_evaluator_identity",
            "expression_grammar_identity",
            "external_output_validator_identity",
            "identity",
            "marking_validator_identity",
            "ordering_policy_identity",
            "transition_enabler_identity",
            "transition_firer_identity",
            "value_model_identity",
        },
    )
    profile = ExperimentalWorkflowCpnExecutionProfile(
        value_model_identity=exact_text(state["value_model_identity"]),
        expression_grammar_identity=exact_text(
            state["expression_grammar_identity"]
        ),
        definition_validator_identity=exact_text(
            state["definition_validator_identity"]
        ),
        marking_validator_identity=exact_text(
            state["marking_validator_identity"]
        ),
        expression_evaluator_identity=exact_text(
            state["expression_evaluator_identity"]
        ),
        transition_enabler_identity=exact_text(
            state["transition_enabler_identity"]
        ),
        ordering_policy_identity=exact_text(state["ordering_policy_identity"]),
        binding_selector_identity=exact_text(
            state["binding_selector_identity"]
        ),
        external_output_validator_identity=exact_text(
            state["external_output_validator_identity"]
        ),
        transition_firer_identity=exact_text(
            state["transition_firer_identity"]
        ),
    )
    if profile.identity.value != exact_text(state["identity"]):
        raise ValueError("execution profile identity differs from its fields")
    return profile


def _reconstruct_bundle(
    value: ExperimentalWorkflowPureActionCpnReplayBundle,
) -> ExperimentalWorkflowPureActionCpnReplayBundle:
    if type(value) is not ExperimentalWorkflowPureActionCpnReplayBundle:
        raise TypeError(
            "value must be ExperimentalWorkflowPureActionCpnReplayBundle"
        )
    reconstructed = ExperimentalWorkflowPureActionCpnReplayBundle(
        cpn_plan_identity=value.cpn_plan_identity,
        input_plan_identity=value.input_plan_identity,
        execution_profile=value.execution_profile,
        definition_representation_profile_identity=(
            value.definition_representation_profile_identity
        ),
        definition_bytes=value.definition_bytes,
        predecessor_marking_representation_profile_identity=(
            value.predecessor_marking_representation_profile_identity
        ),
        predecessor_marking_bytes=value.predecessor_marking_bytes,
        successor_marking_representation_profile_identity=(
            value.successor_marking_representation_profile_identity
        ),
        successor_marking_bytes=value.successor_marking_bytes,
        transition_identity=value.transition_identity,
        selected_binding=value.selected_binding,
        directive_identity=value.directive_identity,
        external_output_binding=value.external_output_binding,
        expected_firing_result_identity=value.expected_firing_result_identity,
    )
    if reconstructed != value:
        raise ValueError("CPN replay bundle differs after reconstruction")
    return reconstructed


def _base64_encode(value: bytes) -> str:
    if type(value) is not bytes:
        raise TypeError("represented CPN state must be bytes")
    return base64.b64encode(value).decode("ascii")


def _base64_decode(value: object) -> bytes:
    if type(value) is not str or not value:
        raise TypeError("represented CPN state must be a nonempty string")
    if len(value) > _MAX_BUNDLE_BYTES:
        raise ValueError("represented CPN state exceeds its text bound")
    text = value
    try:
        encoded = text.encode("ascii")
        decoded = base64.b64decode(encoded, validate=True)
    except (UnicodeEncodeError, ValueError, binascii.Error) as exc:
        raise ValueError("represented CPN state must be strict Base64") from exc
    if base64.b64encode(decoded).decode("ascii") != text:
        raise ValueError("represented CPN state must be canonical Base64")
    return decoded


__all__ = ["ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec"]
