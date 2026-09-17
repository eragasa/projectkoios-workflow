"""Identity-closed pure firing for generic colored Petri nets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from itertools import product
from string import hexdigits
from typing import final

from .definitions import (
    ColoredPetriNetArcDefinition,
    ColoredPetriNetArcIdentity,
    ColoredPetriNetDefinition,
)
from .enablement import (
    ColoredPetriNetEnablementResult,
    ColoredPetriNetTransitionEnabler,
    _represented_state,
)
from .expressions import (
    ColoredPetriNetExpressionEvaluator,
    ColoredPetriNetInputMode,
    ColoredPetriNetTokenPattern,
)
from .markings import (
    ColoredPetriNetBinding,
    ColoredPetriNetMarking,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetPlaceMarking,
    ColoredPetriNetTransitionIdentity,
)
from .selection import (
    ColoredPetriNetBindingSelector,
    ColoredPetriNetSelectionDirectiveIdentity,
    ColoredPetriNetSelectionOutcomeKind,
    ColoredPetriNetSelectionResult,
)
from .validation import (
    ColoredPetriNetDefinitionValidator,
    ColoredPetriNetMarkingValidator,
    ColoredPetriNetValidationIssue,
)
from .values import (
    ColoredPetriNetToken,
    ColoredPetriNetTokenIdentity,
    ColoredPetriNetValueKind,
)


def _digest(payload: dict[str, object]) -> str:
    """Return one domain-owned canonical SHA-256 digest."""
    return sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def _value_state(value: object) -> object:
    """Return one canonical JSON-safe active generic value."""
    if type(value) is float:
        return value.hex()
    if type(value) is tuple:
        return list(value)
    if type(value) is int:
        return str(value)
    return value


def _binding_state(binding: ColoredPetriNetBinding) -> dict[str, object]:
    """Return canonical JSON-safe binding state for identity derivation."""
    return {
        "transition": binding.transition_identity.value,
        "assignments": [
            {
                "variable": item.variable_identity.value,
                "kind": item.value.kind.value,
                "value": _value_state(item.value.value),
            }
            for item in binding.assignments
        ],
    }


def _token_state(token: ColoredPetriNetToken) -> dict[str, object]:
    """Return canonical JSON-safe token state for identity derivation."""
    active = _value_state(token.value.value)
    return {
        "color": token.color_identity.value,
        "kind": token.value.kind.value,
        "value": active,
        "identity": None
        if token.token_identity is None
        else token.token_identity.value,
    }


@dataclass(frozen=True, slots=True)
class ColoredPetriNetFiringResultIdentity:
    """Content identity of one closed firing result."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact lowercase SHA-256 spelling."""
        if type(self.value) is not str:
            raise TypeError("firing result identity value must be a string")
        if (
            len(self.value) != 64
            or self.value != self.value.lower()
            or any(character not in hexdigits for character in self.value)
        ):
            raise ValueError(
                "firing result identity must be a lowercase SHA-256 digest"
            )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetTransitionFirerIdentity:
    """Nominal identity of exact pure-firing semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError("transition firer identity value must be a string")
        if not self.value:
            raise ValueError("transition firer identity value must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetTokenOccurrence:
    """One exact predecessor token occurrence used by an input inscription."""

    arc_identity: ColoredPetriNetArcIdentity
    place_identity: ColoredPetriNetPlaceIdentity
    pattern_index: int
    occurrence_ordinal: int
    token: ColoredPetriNetToken

    def __post_init__(self) -> None:
        """Validate exact nominal occurrence coordinates."""
        expected = (
            (self.arc_identity, ColoredPetriNetArcIdentity, "arc_identity"),
            (self.place_identity, ColoredPetriNetPlaceIdentity, "place_identity"),
            (self.token, ColoredPetriNetToken, "token"),
        )
        for value, nominal_type, name in expected:
            if type(value) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        for name in ("pattern_index", "occurrence_ordinal"):
            value = getattr(self, name)
            if type(value) is not int:
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be nonnegative")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetInhibitorEvaluation:
    """One audited nonbinding inhibitor absence evaluation."""

    arc_identity: ColoredPetriNetArcIdentity
    place_identity: ColoredPetriNetPlaceIdentity
    pattern_index: int
    matching_count: int

    def __post_init__(self) -> None:
        """Validate exact nonnegative inhibitor audit coordinates."""
        if type(self.arc_identity) is not ColoredPetriNetArcIdentity:
            raise TypeError("arc_identity must be ColoredPetriNetArcIdentity")
        if type(self.place_identity) is not ColoredPetriNetPlaceIdentity:
            raise TypeError("place_identity must be ColoredPetriNetPlaceIdentity")
        for name in ("pattern_index", "matching_count"):
            value = getattr(self, name)
            if type(value) is not int:
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be nonnegative")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetProducedToken:
    """One exact produced token and destination output coordinate."""

    arc_identity: ColoredPetriNetArcIdentity
    place_identity: ColoredPetriNetPlaceIdentity
    template_index: int
    token: ColoredPetriNetToken

    def __post_init__(self) -> None:
        """Validate exact produced-token audit state."""
        if type(self.arc_identity) is not ColoredPetriNetArcIdentity:
            raise TypeError("arc_identity must be ColoredPetriNetArcIdentity")
        if type(self.place_identity) is not ColoredPetriNetPlaceIdentity:
            raise TypeError("place_identity must be ColoredPetriNetPlaceIdentity")
        if type(self.template_index) is not int:
            raise TypeError("template_index must be an integer")
        if self.template_index < 0:
            raise ValueError("template_index must be nonnegative")
        if type(self.token) is not ColoredPetriNetToken:
            raise TypeError("token must be ColoredPetriNetToken")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetFiringInput:
    """Exact immutable derivation inputs for one pure firing attempt."""

    definition: ColoredPetriNetDefinition
    transition_identity: ColoredPetriNetTransitionIdentity
    predecessor_marking: ColoredPetriNetMarking
    enablement_result: ColoredPetriNetEnablementResult
    selection_result: ColoredPetriNetSelectionResult
    selected_binding: ColoredPetriNetBinding
    directive_identity: ColoredPetriNetSelectionDirectiveIdentity | None
    external_output_binding: ColoredPetriNetBinding

    def __post_init__(self) -> None:
        """Validate exact public nominal argument types only."""
        expected = (
            ("definition", ColoredPetriNetDefinition),
            ("transition_identity", ColoredPetriNetTransitionIdentity),
            ("predecessor_marking", ColoredPetriNetMarking),
            ("enablement_result", ColoredPetriNetEnablementResult),
            ("selection_result", ColoredPetriNetSelectionResult),
            ("selected_binding", ColoredPetriNetBinding),
            ("external_output_binding", ColoredPetriNetBinding),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        if self.directive_identity is not None and (
            type(self.directive_identity)
            is not ColoredPetriNetSelectionDirectiveIdentity
        ):
            raise TypeError(
                "directive_identity must be ColoredPetriNetSelectionDirectiveIdentity "
                "or None"
            )


class ColoredPetriNetFiringFailureCode(StrEnum):
    """Closed pure-firing failure codes."""

    INVALID_DEFINITION = "invalid_definition"
    INVALID_PREDECESSOR_MARKING = "invalid_predecessor_marking"
    ENABLEMENT_MISMATCH = "enablement_mismatch"
    SELECTION_MISMATCH = "selection_mismatch"
    DIRECTIVE_MISMATCH = "directive_mismatch"
    TRANSITION_OR_BINDING_MISMATCH = "transition_or_binding_mismatch"
    EXTERNAL_OUTPUT_BINDING_MISMATCH = "external_output_binding_mismatch"
    INPUT_OCCURRENCE_RECONSTRUCTION_FAILED = "input_occurrence_reconstruction_failed"
    OUTPUT_EVALUATION_FAILED = "output_evaluation_failed"
    PRODUCED_TOKEN_INVALID = "produced_token_invalid"
    TOKEN_IDENTITY_COLLISION = "token_identity_collision"


@dataclass(frozen=True, slots=True)
class ColoredPetriNetFiringFailureIdentity:
    """Nominal identity of the failure variant of one firing result."""

    result_identity: ColoredPetriNetFiringResultIdentity

    def __post_init__(self) -> None:
        """Bind to one exact firing-result identity."""
        if type(self.result_identity) is not ColoredPetriNetFiringResultIdentity:
            raise TypeError(
                "result_identity must be ColoredPetriNetFiringResultIdentity"
            )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetFiringFailure:
    """Structured pure-firing failure with no successor."""

    identity: ColoredPetriNetFiringFailureIdentity
    code: ColoredPetriNetFiringFailureCode
    operation_phase: str
    expected_condition: str
    observed_condition: str
    diagnostic: str
    validation_issues: tuple[ColoredPetriNetValidationIssue, ...] = ()
    claim_boundary: tuple[str, ...] = (
        "pure generic firing only",
        "no external effect or authority",
        "no scientific acceptance",
    )

    def __post_init__(self) -> None:
        """Validate immutable structured failure state."""
        if type(self.identity) is not ColoredPetriNetFiringFailureIdentity:
            raise TypeError("identity must be ColoredPetriNetFiringFailureIdentity")
        if not isinstance(self.code, ColoredPetriNetFiringFailureCode):
            raise TypeError("code must be ColoredPetriNetFiringFailureCode")
        for name in (
            "operation_phase",
            "expected_condition",
            "observed_condition",
            "diagnostic",
        ):
            value = getattr(self, name)
            if type(value) is not str:
                raise TypeError(f"{name} must be a string")
            if not value:
                raise ValueError(f"{name} must not be empty")
        if type(self.validation_issues) is not tuple or any(
            type(item) is not ColoredPetriNetValidationIssue
            for item in self.validation_issues
        ):
            raise TypeError(
                "validation_issues must be a tuple of ColoredPetriNetValidationIssue"
            )
        if type(self.claim_boundary) is not tuple or any(
            type(item) is not str for item in self.claim_boundary
        ):
            raise TypeError("claim_boundary must be a tuple of strings")
        if not self.claim_boundary or any(not item for item in self.claim_boundary):
            raise ValueError("claim_boundary must contain nonempty strings")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetFiringAudit:
    """Complete immutable occurrence and output audit for successful firing."""

    consumed_occurrences: tuple[ColoredPetriNetTokenOccurrence, ...]
    read_occurrences: tuple[ColoredPetriNetTokenOccurrence, ...]
    inhibitor_evaluations: tuple[ColoredPetriNetInhibitorEvaluation, ...]
    produced_tokens: tuple[ColoredPetriNetProducedToken, ...]
    firer_identity: ColoredPetriNetTransitionFirerIdentity

    def __post_init__(self) -> None:
        """Validate exact immutable audit collections."""
        collections = (
            ("consumed_occurrences", ColoredPetriNetTokenOccurrence),
            ("read_occurrences", ColoredPetriNetTokenOccurrence),
            ("inhibitor_evaluations", ColoredPetriNetInhibitorEvaluation),
            ("produced_tokens", ColoredPetriNetProducedToken),
        )
        for name, member_type in collections:
            values = getattr(self, name)
            if type(values) is not tuple or any(
                type(item) is not member_type for item in values
            ):
                raise TypeError(f"{name} must be a tuple of {member_type.__name__}")
        if type(self.firer_identity) is not ColoredPetriNetTransitionFirerIdentity:
            raise TypeError(
                "firer_identity must be ColoredPetriNetTransitionFirerIdentity"
            )


class ColoredPetriNetFiringOutcomeKind(StrEnum):
    """Closed success or failure firing outcome."""

    SUCCESS = "success"
    FAILURE = "failure"


@dataclass(frozen=True, slots=True)
class ColoredPetriNetFiringResult:
    """One identity-bound pure-firing success or failure."""

    identity: ColoredPetriNetFiringResultIdentity
    firing_input: ColoredPetriNetFiringInput
    outcome: ColoredPetriNetFiringOutcomeKind
    successor_marking: ColoredPetriNetMarking | None = None
    audit: ColoredPetriNetFiringAudit | None = None
    failure: ColoredPetriNetFiringFailure | None = None

    def __post_init__(self) -> None:
        """Enforce exact nominal types and one closed outcome."""
        if type(self.identity) is not ColoredPetriNetFiringResultIdentity:
            raise TypeError("identity must be ColoredPetriNetFiringResultIdentity")
        if type(self.firing_input) is not ColoredPetriNetFiringInput:
            raise TypeError("firing_input must be ColoredPetriNetFiringInput")
        if not isinstance(self.outcome, ColoredPetriNetFiringOutcomeKind):
            raise TypeError("outcome must be ColoredPetriNetFiringOutcomeKind")
        valid = (
            self.outcome is ColoredPetriNetFiringOutcomeKind.SUCCESS
            and type(self.successor_marking) is ColoredPetriNetMarking
            and type(self.audit) is ColoredPetriNetFiringAudit
            and self.failure is None
        ) or (
            self.outcome is ColoredPetriNetFiringOutcomeKind.FAILURE
            and self.successor_marking is None
            and self.audit is None
            and type(self.failure) is ColoredPetriNetFiringFailure
        )
        if not valid:
            raise ValueError("firing fields do not match the outcome variant")
        if self.failure is not None and (
            self.failure.identity.result_identity != self.identity
        ):
            raise ValueError("failure identity must bind this result identity")


_FIRER_IDENTITY = ColoredPetriNetTransitionFirerIdentity(
    "colored-petri-net-transition-firer-v1"
)


@final
class ColoredPetriNetTransitionFirer:
    """ActionObject producing one pure identity-closed successor marking."""

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Reject subclass-injected firing policy."""
        raise TypeError("ColoredPetriNetTransitionFirer does not support subclasses")

    def execute(
        self, firing_input: ColoredPetriNetFiringInput
    ) -> ColoredPetriNetFiringResult:
        """Validate the complete derivation and return success or structured failure."""
        if type(firing_input) is not ColoredPetriNetFiringInput:
            raise TypeError("firing_input must be ColoredPetriNetFiringInput")
        definition = firing_input.definition
        marking = firing_input.predecessor_marking
        definition_validation = ColoredPetriNetDefinitionValidator().execute(definition)
        if not definition_validation.is_valid:
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.INVALID_DEFINITION,
                "definition_validation",
                "a structurally valid definition",
                "definition validation returned findings",
                definition_validation.issues,
            )
        marking_validation = ColoredPetriNetMarkingValidator().execute(
            definition, marking
        )
        if not marking_validation.is_valid:
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.INVALID_PREDECESSOR_MARKING,
                "marking_validation",
                "a compatible complete predecessor marking",
                "marking validation returned findings",
                marking_validation.issues,
            )
        recomputed_enablement = ColoredPetriNetTransitionEnabler().execute(
            definition, marking
        )
        if recomputed_enablement != firing_input.enablement_result:
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.ENABLEMENT_MISMATCH,
                "enablement_replay",
                "replay-equal complete enablement",
                "supplied enablement differs from recomputation",
            )
        directive = firing_input.selection_result.directive
        recomputed_selection = ColoredPetriNetBindingSelector().execute(
            definition, recomputed_enablement, directive
        )
        if recomputed_selection != firing_input.selection_result:
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.SELECTION_MISMATCH,
                "selection_replay",
                "replay-equal exact selection",
                "supplied selection differs from recomputation",
            )
        if (
            firing_input.selection_result.outcome
            is not (ColoredPetriNetSelectionOutcomeKind.SELECTED)
            or firing_input.selection_result.selected_binding
            != firing_input.selected_binding
        ):
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.TRANSITION_OR_BINDING_MISMATCH,
                "selected_binding_validation",
                "one exact selected binding",
                "firing binding is not the selected binding",
            )
        if (
            firing_input.directive_identity
            != firing_input.selection_result.directive_identity
        ):
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.DIRECTIVE_MISMATCH,
                "directive_validation",
                "the exact selection directive identity or absence",
                "firing directive identity differs from selection",
            )
        binding = firing_input.selected_binding
        transition = next(
            (
                item
                for item in definition.transitions
                if item.identity == binding.transition_identity
            ),
            None,
        )
        if (
            transition is None
            or firing_input.transition_identity != binding.transition_identity
        ):
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.TRANSITION_OR_BINDING_MISMATCH,
                "transition_validation",
                "the selected defined transition",
                "transition identity differs from selected binding",
            )
        external = firing_input.external_output_binding
        if (
            external.transition_identity != transition.identity
            or tuple(item.variable_identity for item in external.assignments)
            != transition.external_output_variable_identities
        ):
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.EXTERNAL_OUTPUT_BINDING_MISMATCH,
                "external_output_validation",
                "exact declared external-output assignments in order",
                "external-output binding is incomplete, extra, reordered, "
                "or mismatched",
            )
        occurrences = self._reconstruct(definition, marking, binding)
        if occurrences is None:
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.INPUT_OCCURRENCE_RECONSTRUCTION_FAILED,
                "input_reconstruction",
                "one canonical feasible occurrence assignment",
                "selected value binding cannot be reconstructed",
            )
        consumed, read, inhibitors = occurrences
        combined = ColoredPetriNetBinding(
            transition.identity, binding.assignments + external.assignments
        )
        produced: list[ColoredPetriNetProducedToken] = []
        evaluator = ColoredPetriNetExpressionEvaluator()
        try:
            for arc in definition.arcs:
                if (
                    arc.transition_identity != transition.identity
                    or arc.output_inscription is None
                ):
                    continue
                for index, template in enumerate(arc.output_inscription.templates):
                    value = evaluator.evaluate_value(
                        template.value_expression, combined
                    )
                    identity = None
                    if template.token_identity_expression is not None:
                        identity_value = evaluator.evaluate_value(
                            template.token_identity_expression, combined
                        )
                        if identity_value.kind is not ColoredPetriNetValueKind.STRING:
                            raise TypeError(
                                "token identity expression must produce string"
                            )
                        assert type(identity_value.value) is str
                        identity = ColoredPetriNetTokenIdentity(identity_value.value)
                    token = ColoredPetriNetToken(
                        template.color_identity, value, identity
                    )
                    produced.append(
                        ColoredPetriNetProducedToken(
                            arc.identity, arc.place_identity, index, token
                        )
                    )
        except (KeyError, TypeError, ValueError) as exc:
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.OUTPUT_EVALUATION_FAILED,
                "output_evaluation",
                "well-typed total output templates",
                f"{type(exc).__name__}: {exc}",
            )
        consumed_coordinates = {
            (item.place_identity, item.occurrence_ordinal) for item in consumed
        }
        retained_identities = {
            token.token_identity
            for place in marking.places
            for index, token in enumerate(place.tokens)
            if (place.place_identity, index) not in consumed_coordinates
            and token.token_identity is not None
        }
        produced_identities = tuple(
            item.token.token_identity
            for item in produced
            if item.token.token_identity is not None
        )
        if len(set(produced_identities)) != len(produced_identities) or (
            retained_identities & set(produced_identities)
        ):
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.TOKEN_IDENTITY_COLLISION,
                "produced_identity_validation",
                "new unique identities or identities released by consumption",
                "produced identity is duplicate or collides with a retained token",
            )
        produced_by_place: dict[
            ColoredPetriNetPlaceIdentity, list[ColoredPetriNetToken]
        ] = {}
        for item in produced:
            produced_by_place.setdefault(item.place_identity, []).append(item.token)
        successor_places = tuple(
            ColoredPetriNetPlaceMarking(
                place.place_identity,
                tuple(
                    token
                    for index, token in enumerate(place.tokens)
                    if (place.place_identity, index) not in consumed_coordinates
                )
                + tuple(produced_by_place.get(place.place_identity, ())),
            )
            for place in marking.places
        )
        successor_identity = ColoredPetriNetMarkingIdentity(
            _digest(
                {
                    "domain": "ksdft2effmass.petrinet.colored.successor-marking-v1",
                    "definition": definition.identity.value,
                    "predecessor": marking.identity.value,
                    "places": [
                        {
                            "place": place.place_identity.value,
                            "tokens": [_token_state(token) for token in place.tokens],
                        }
                        for place in successor_places
                    ],
                }
            )
        )
        successor = ColoredPetriNetMarking(
            successor_identity, definition.identity, successor_places
        )
        if (
            not ColoredPetriNetMarkingValidator()
            .execute(definition, successor)
            .is_valid
        ):
            return self._failure(
                firing_input,
                ColoredPetriNetFiringFailureCode.PRODUCED_TOKEN_INVALID,
                "successor_validation",
                "a definition-compatible successor marking",
                "produced tokens make the successor invalid",
            )
        audit = ColoredPetriNetFiringAudit(
            consumed, read, inhibitors, tuple(produced), _FIRER_IDENTITY
        )
        result_identity = ColoredPetriNetFiringResultIdentity(
            _digest(
                {
                    "domain": "ksdft2effmass.petrinet.colored.firing-result-v1",
                    "enablement": firing_input.enablement_result.identity.value,
                    "selection": firing_input.selection_result.identity.value,
                    "transition": firing_input.transition_identity.value,
                    "selected_binding": _binding_state(firing_input.selected_binding),
                    "external_output_binding": _binding_state(
                        firing_input.external_output_binding
                    ),
                    "directive": (
                        None
                        if firing_input.directive_identity is None
                        else firing_input.directive_identity.value
                    ),
                    "successor": successor.identity.value,
                    "consumed": [self._occurrence_state(item) for item in consumed],
                    "read": [self._occurrence_state(item) for item in read],
                    "inhibitors": [
                        {
                            "arc": item.arc_identity.value,
                            "place": item.place_identity.value,
                            "pattern": item.pattern_index,
                            "matching_count": item.matching_count,
                        }
                        for item in inhibitors
                    ],
                    "produced": [
                        {
                            "arc": item.arc_identity.value,
                            "place": item.place_identity.value,
                            "index": item.template_index,
                            "token": _token_state(item.token),
                        }
                        for item in produced
                    ],
                    "firer": _FIRER_IDENTITY.value,
                }
            )
        )
        return ColoredPetriNetFiringResult(
            result_identity,
            firing_input,
            ColoredPetriNetFiringOutcomeKind.SUCCESS,
            successor,
            audit,
        )

    @staticmethod
    def _reconstruct(
        definition: ColoredPetriNetDefinition,
        marking: ColoredPetriNetMarking,
        binding: ColoredPetriNetBinding,
    ) -> (
        tuple[
            tuple[ColoredPetriNetTokenOccurrence, ...],
            tuple[ColoredPetriNetTokenOccurrence, ...],
            tuple[ColoredPetriNetInhibitorEvaluation, ...],
        ]
        | None
    ):
        """Return the least feasible occurrence assignment for one value binding."""
        values = {item.variable_identity: item.value for item in binding.assignments}
        by_place = {item.place_identity: item.tokens for item in marking.places}
        demands: list[
            tuple[
                ColoredPetriNetArcDefinition,
                ColoredPetriNetInputMode,
                int,
                ColoredPetriNetTokenPattern,
            ]
        ] = []
        candidates: list[tuple[tuple[int, ColoredPetriNetToken], ...]] = []
        inhibitors: list[ColoredPetriNetInhibitorEvaluation] = []
        for arc in definition.arcs:
            if (
                arc.transition_identity != binding.transition_identity
                or arc.input_inscription is None
            ):
                continue
            inscription = arc.input_inscription
            tokens = by_place[arc.place_identity]
            if inscription.mode is ColoredPetriNetInputMode.INHIBIT:
                for index, pattern in enumerate(inscription.patterns):
                    count = sum(
                        token.color_identity in pattern.allowed_color_identities
                        for token in tokens
                    )
                    inhibitors.append(
                        ColoredPetriNetInhibitorEvaluation(
                            arc.identity, arc.place_identity, index, count
                        )
                    )
                    if count:
                        return None
                continue
            for index, pattern in enumerate(inscription.patterns):
                assert type(pattern) is ColoredPetriNetTokenPattern
                expected = values[pattern.variable_identity]
                demands.append((arc, inscription.mode, index, pattern))
                candidates.append(
                    tuple(
                        (ordinal, token)
                        for ordinal, token in enumerate(tokens)
                        if token.color_identity in pattern.allowed_color_identities
                        and token.value == expected
                    )
                )
        if any(not items for items in candidates):
            return None
        for selected in product(*candidates) if candidates else [()]:
            reserved: set[tuple[object, object, int]] = set()
            consumed: list[ColoredPetriNetTokenOccurrence] = []
            read: list[ColoredPetriNetTokenOccurrence] = []
            feasible = True
            for (arc, mode, index, _), (ordinal, token) in zip(
                demands, selected, strict=True
            ):
                key = (arc.place_identity, mode, ordinal)
                if key in reserved:
                    feasible = False
                    break
                reserved.add(key)
                occurrence = ColoredPetriNetTokenOccurrence(
                    arc.identity, arc.place_identity, index, ordinal, token
                )
                (consumed if mode is ColoredPetriNetInputMode.CONSUME else read).append(
                    occurrence
                )
            if feasible:
                return tuple(consumed), tuple(read), tuple(inhibitors)
        return None

    @staticmethod
    def _occurrence_state(item: ColoredPetriNetTokenOccurrence) -> dict[str, object]:
        """Return canonical identity state for one occurrence audit."""
        return {
            "arc": item.arc_identity.value,
            "place": item.place_identity.value,
            "pattern": item.pattern_index,
            "ordinal": item.occurrence_ordinal,
            "token": _token_state(item.token),
        }

    @staticmethod
    def _failure(
        firing_input: ColoredPetriNetFiringInput,
        code: ColoredPetriNetFiringFailureCode,
        phase: str,
        expected: str,
        observed: str,
        issues: tuple[ColoredPetriNetValidationIssue, ...] = (),
    ) -> ColoredPetriNetFiringResult:
        """Return one content-identified closed failure with no successor."""
        result_identity = ColoredPetriNetFiringResultIdentity(
            _digest(
                {
                    "domain": "ksdft2effmass.petrinet.colored.firing-result-v1",
                    "firing_input": _represented_state(firing_input),
                    "definition": firing_input.definition.identity.value,
                    "predecessor": firing_input.predecessor_marking.identity.value,
                    "enablement": firing_input.enablement_result.identity.value,
                    "selection": firing_input.selection_result.identity.value,
                    "transition": firing_input.transition_identity.value,
                    "selected_binding": _binding_state(firing_input.selected_binding),
                    "external_output_binding": _binding_state(
                        firing_input.external_output_binding
                    ),
                    "directive": (
                        None
                        if firing_input.directive_identity is None
                        else firing_input.directive_identity.value
                    ),
                    "code": code.value,
                    "phase": phase,
                    "expected": expected,
                    "observed": observed,
                    "issues": [
                        (
                            item.path,
                            item.code.value,
                            item.related_identities,
                            item.message,
                        )
                        for item in issues
                    ],
                    "firer": _FIRER_IDENTITY.value,
                }
            )
        )
        failure = ColoredPetriNetFiringFailure(
            ColoredPetriNetFiringFailureIdentity(result_identity),
            code,
            phase,
            expected,
            observed,
            "firing produced no successor",
            issues,
        )
        return ColoredPetriNetFiringResult(
            result_identity,
            firing_input,
            ColoredPetriNetFiringOutcomeKind.FAILURE,
            failure=failure,
        )
