"""Canonical transcript and pure refiring for committed CPN candidates."""

from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass, field
from enum import StrEnum
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
    experimental_shadow_cpn_execution_profile,
)
from projectkoios.workflow.compilation._cpn_representation import (
    closed_array,
    closed_object,
    exact_text,
    value_from_state,
    value_state,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingSelector,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetFiringInput,
    ColoredPetriNetFiringOutcomeKind,
    ColoredPetriNetFiringResult,
    ColoredPetriNetFiringResultIdentity,
    ColoredPetriNetSelectionDirective,
    ColoredPetriNetSelectionDirectiveIdentity,
    ColoredPetriNetSelectionOutcomeKind,
    ColoredPetriNetTransitionEnabler,
    ColoredPetriNetTransitionFirer,
    ColoredPetriNetTransitionIdentity,
)

_BUNDLE_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-cpn-replay-bundle:0"
)
_BUNDLE_SCHEMA = (
    "projectkoios.workflow.experimental-pure-action-cpn-replay-json:0"
)
_MAX_BUNDLE_BYTES = 64 * 1024 * 1024
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


class ExperimentalWorkflowPureActionCpnReplayStatus(StrEnum):
    """Closed result of exact in-memory pure-CPN transcript replay."""

    REPLAYED = "replayed"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCpnReplayResult:
    """Expose a pure result only after exact transcript refiring."""

    status: ExperimentalWorkflowPureActionCpnReplayStatus
    bundle_identity: (
        ExperimentalWorkflowPureActionCpnReplayBundleIdentity | None
    )
    firing_result: ColoredPetriNetFiringResult | None
    bundle_sha256: str | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.status)
            is not ExperimentalWorkflowPureActionCpnReplayStatus
        ):
            raise TypeError(
                "status must be ExperimentalWorkflowPureActionCpnReplayStatus"
            )
        if type(self.diagnostics) is not tuple or any(
            type(item) is not str or not item or len(item) > 128
            for item in self.diagnostics
        ):
            raise TypeError("diagnostics must contain bounded nonempty strings")
        if (
            self.status
            is ExperimentalWorkflowPureActionCpnReplayStatus.REPLAYED
        ):
            if type(self.bundle_identity) is not (
                ExperimentalWorkflowPureActionCpnReplayBundleIdentity
            ):
                raise TypeError("replayed status requires a bundle identity")
            if type(self.firing_result) is not ColoredPetriNetFiringResult:
                raise TypeError("replayed status requires a firing result")
            _validate_sha256(self.bundle_sha256, "bundle SHA-256")
            if self.diagnostics:
                raise ValueError("replayed status prohibits diagnostics")
        elif (
            self.bundle_identity is not None
            or self.firing_result is not None
            or self.bundle_sha256 is not None
        ):
            raise ValueError("non-replayed status prohibits replayed state")
        elif not self.diagnostics:
            raise ValueError("non-replayed status requires diagnostics")


@final
class ExperimentalWorkflowPureActionCpnReplayService:
    """Decode and refire one pure CPN transcript without owner invocation."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionCpnReplayService is not subclassable"
        )

    def execute(
        self, value: bytes
    ) -> ExperimentalWorkflowPureActionCpnReplayResult:
        """Refire only under the exact supported retained profile."""
        try:
            bundle = (
                ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().decode(
                    value
                )
            )
        except (TypeError, ValueError) as exc:
            return _replay_failure(
                ExperimentalWorkflowPureActionCpnReplayStatus.CORRUPT,
                str(exc) or "CPN replay bundle decoding failed",
            )
        if (
            bundle.execution_profile
            != experimental_shadow_cpn_execution_profile()
        ):
            return _replay_failure(
                ExperimentalWorkflowPureActionCpnReplayStatus.INCOMPATIBLE,
                "CPN execution profile is unsupported",
            )
        try:
            definition = ExperimentalWorkflowCpnDefinitionDecoder().decode(
                bundle.definition_bytes
            )
            predecessor = ExperimentalWorkflowCpnMarkingDecoder().decode(
                bundle.predecessor_marking_bytes
            )
            expected_successor = ExperimentalWorkflowCpnMarkingDecoder().decode(
                bundle.successor_marking_bytes
            )
            enablement = ColoredPetriNetTransitionEnabler().execute(
                definition, predecessor
            )
            directive = None
            if bundle.directive_identity is not None:
                directive = ColoredPetriNetSelectionDirective(
                    enablement.identity,
                    bundle.selected_binding,
                )
                if directive.identity != bundle.directive_identity:
                    raise ValueError("selection directive identity differs")
            selection = ColoredPetriNetBindingSelector().execute(
                definition,
                enablement,
                directive,
            )
            if (
                selection.outcome
                is not ColoredPetriNetSelectionOutcomeKind.SELECTED
                or selection.selected_binding != bundle.selected_binding
            ):
                raise ValueError(
                    "retained binding is not selected during replay"
                )
            firing_input = ColoredPetriNetFiringInput(
                definition=definition,
                transition_identity=bundle.transition_identity,
                predecessor_marking=predecessor,
                enablement_result=enablement,
                selection_result=selection,
                selected_binding=bundle.selected_binding,
                directive_identity=bundle.directive_identity,
                external_output_binding=bundle.external_output_binding,
            )
            result = ColoredPetriNetTransitionFirer().execute(firing_input)
            if (
                result.outcome is not ColoredPetriNetFiringOutcomeKind.SUCCESS
                or result.successor_marking != expected_successor
                or result.identity != bundle.expected_firing_result_identity
            ):
                raise ValueError(
                    "pure CPN refiring differs from retained result"
                )
        except (KeyError, TypeError, ValueError) as exc:
            return _replay_failure(
                ExperimentalWorkflowPureActionCpnReplayStatus.CORRUPT,
                str(exc) or "pure CPN refiring failed",
            )
        except Exception:
            return _replay_failure(
                ExperimentalWorkflowPureActionCpnReplayStatus.ERROR,
                "pure CPN replay error",
            )
        return ExperimentalWorkflowPureActionCpnReplayResult(
            status=ExperimentalWorkflowPureActionCpnReplayStatus.REPLAYED,
            bundle_identity=bundle.identity,
            firing_result=result,
            bundle_sha256=sha256(value).hexdigest(),
            diagnostics=(),
        )


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


def _binding_bytes(value: ColoredPetriNetBinding) -> bytes:
    return json.dumps(
        _binding_state(value),
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


def _replay_failure(
    status: ExperimentalWorkflowPureActionCpnReplayStatus,
    diagnostic: str,
) -> ExperimentalWorkflowPureActionCpnReplayResult:
    return ExperimentalWorkflowPureActionCpnReplayResult(
        status=status,
        bundle_identity=None,
        firing_result=None,
        bundle_sha256=None,
        diagnostics=(diagnostic[:128],),
    )


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
    "ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec",
    "ExperimentalWorkflowPureActionCpnReplayResult",
    "ExperimentalWorkflowPureActionCpnReplayService",
    "ExperimentalWorkflowPureActionCpnReplayStatus",
]
