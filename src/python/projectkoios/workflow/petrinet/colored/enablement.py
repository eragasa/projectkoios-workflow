"""Complete deterministic enablement for generic colored Petri nets.

Enablement is a pure ActionObject operation over one exact definition and
marking. Private occurrence coordinates enforce multiset capacity; public
bindings contain only definition-declared variable/value assignments. The
operation performs no selection, firing, Task invocation, external effect,
persistence, authority decision, or scientific calculation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, fields, is_dataclass
from enum import StrEnum
from hashlib import sha256
from itertools import product
from string import hexdigits
from typing import Any, final

from .definitions import ColoredPetriNetDefinition, ColoredPetriNetSelectionPolicy
from .expressions import (
    ColoredPetriNetExpressionEvaluator,
    ColoredPetriNetInputMode,
    ColoredPetriNetTokenPattern,
)
from .markings import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetMarking,
    ColoredPetriNetMarkingIdentity,
)
from .validation import (
    ColoredPetriNetDefinitionValidator,
    ColoredPetriNetMarkingValidator,
    ColoredPetriNetValidationIssue,
)
from .values import ColoredPetriNetToken, ColoredPetriNetValue, ColoredPetriNetValueKind


@dataclass(frozen=True, slots=True)
class ColoredPetriNetEnablementResultIdentity:
    """Content identity of one complete enablement operation result.

    ``value`` is the lowercase SHA-256 digest of the enabler-owned canonical
    identity preimage. The digest contract is independent of the deferred public
    result serialization format.
    """

    value: str

    def __post_init__(self) -> None:
        """Require one exact lowercase SHA-256 spelling."""
        if type(self.value) is not str:
            raise TypeError("enablement result identity value must be a string")
        if (
            len(self.value) != 64
            or self.value != self.value.lower()
            or any(character not in hexdigits for character in self.value)
        ):
            raise ValueError(
                "enablement result identity must be a lowercase SHA-256 digest"
            )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetExpressionEvaluatorIdentity:
    """Nominal identity of exact expression semantics used by enablement."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError("expression evaluator identity value must be a string")
        if not self.value:
            raise ValueError("expression evaluator identity value must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetOrderingPolicyIdentity:
    """Nominal identity of exact enablement ordering semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError("ordering policy identity value must be a string")
        if not self.value:
            raise ValueError("ordering policy identity value must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetTransitionEnablerIdentity:
    """Nominal identity of exact transition-enablement semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError("transition enabler identity value must be a string")
        if not self.value:
            raise ValueError("transition enabler identity value must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetEnablementFailureIdentity:
    """Nominal identity of the failure variant of one enablement result."""

    result_identity: ColoredPetriNetEnablementResultIdentity

    def __post_init__(self) -> None:
        """Bind the failure identity to one exact result identity."""
        if type(self.result_identity) is not ColoredPetriNetEnablementResultIdentity:
            raise TypeError(
                "result_identity must be ColoredPetriNetEnablementResultIdentity"
            )


class ColoredPetriNetEnablementFailureCode(StrEnum):
    """Closed operational failure codes for complete enablement."""

    INVALID_DEFINITION = "invalid_definition"
    INVALID_MARKING = "invalid_marking"
    UNSUPPORTED_EXPRESSION_EVALUATOR = "unsupported_expression_evaluator"
    UNSUPPORTED_ORDERING_POLICY = "unsupported_ordering_policy"
    GUARD_EVALUATION_FAILED = "guard_evaluation_failed"


@dataclass(frozen=True, slots=True)
class ColoredPetriNetEnablementFailure:
    """One structured failure with no enabled-binding payload."""

    identity: ColoredPetriNetEnablementFailureIdentity
    code: ColoredPetriNetEnablementFailureCode
    operation_phase: str
    expected_condition: str
    observed_condition: str
    diagnostic: str
    validation_issues: tuple[ColoredPetriNetValidationIssue, ...] = ()
    claim_boundary: tuple[str, ...] = (
        "software enablement only",
        "no firing or external effect",
        "no scientific acceptance",
    )

    def __post_init__(self) -> None:
        """Validate immutable closed failure state."""
        if type(self.identity) is not ColoredPetriNetEnablementFailureIdentity:
            raise TypeError("identity must be ColoredPetriNetEnablementFailureIdentity")
        if not isinstance(self.code, ColoredPetriNetEnablementFailureCode):
            raise TypeError("code must be ColoredPetriNetEnablementFailureCode")
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
class ColoredPetriNetEnablementResult:
    """Closed complete success or failure for one definition and marking."""

    identity: ColoredPetriNetEnablementResultIdentity
    definition_identity: ColoredPetriNetDefinitionIdentity
    selection_policy: ColoredPetriNetSelectionPolicy
    marking_identity: ColoredPetriNetMarkingIdentity
    expression_evaluator_identity: ColoredPetriNetExpressionEvaluatorIdentity
    ordering_policy_identity: ColoredPetriNetOrderingPolicyIdentity
    transition_enabler_identity: ColoredPetriNetTransitionEnablerIdentity
    enabled_bindings: tuple[ColoredPetriNetBinding, ...] | None = None
    failure: ColoredPetriNetEnablementFailure | None = None

    def __post_init__(self) -> None:
        """Enforce exact nominal identities and one closed outcome variant."""
        expected = (
            ("identity", ColoredPetriNetEnablementResultIdentity),
            ("definition_identity", ColoredPetriNetDefinitionIdentity),
            ("selection_policy", ColoredPetriNetSelectionPolicy),
            ("marking_identity", ColoredPetriNetMarkingIdentity),
            (
                "expression_evaluator_identity",
                ColoredPetriNetExpressionEvaluatorIdentity,
            ),
            ("ordering_policy_identity", ColoredPetriNetOrderingPolicyIdentity),
            ("transition_enabler_identity", ColoredPetriNetTransitionEnablerIdentity),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        if self.enabled_bindings is not None and (
            type(self.enabled_bindings) is not tuple
            or any(
                type(item) is not ColoredPetriNetBinding
                for item in self.enabled_bindings
            )
        ):
            raise TypeError(
                "enabled_bindings must be a tuple of ColoredPetriNetBinding or None"
            )
        if self.failure is not None and (
            type(self.failure) is not ColoredPetriNetEnablementFailure
        ):
            raise TypeError("failure must be ColoredPetriNetEnablementFailure or None")
        if (self.enabled_bindings is None) == (self.failure is None):
            raise ValueError(
                "exactly one of enabled_bindings and failure must be present"
            )
        if self.enabled_bindings is not None and len(set(self.enabled_bindings)) != len(
            self.enabled_bindings
        ):
            raise ValueError("enabled_bindings must be unique")
        if self.failure is not None and (
            self.failure.identity.result_identity != self.identity
        ):
            raise ValueError("failure identity must bind this result identity")

    @property
    def is_success(self) -> bool:
        """Return whether this closed result contains enabled bindings."""
        return self.enabled_bindings is not None


_EXPRESSION_EVALUATOR_IDENTITY = ColoredPetriNetExpressionEvaluatorIdentity(
    "colored-petri-net-expression-evaluator-v1"
)
_ORDERING_POLICY_IDENTITY = ColoredPetriNetOrderingPolicyIdentity(
    "colored-petri-net-enablement-order-v1"
)
_TRANSITION_ENABLER_IDENTITY = ColoredPetriNetTransitionEnablerIdentity(
    "colored-petri-net-transition-enabler-v1"
)


def _value_key(value: ColoredPetriNetValue) -> tuple[str, Any]:
    """Return the deterministic in-memory ordering key."""
    if value.kind is ColoredPetriNetValueKind.NONE:
        return (value.kind.value, ())
    return (value.kind.value, value.value)


def _identity_value(value: ColoredPetriNetValue) -> object:
    """Return the JSON-safe canonical active-value identity representation."""
    if value.kind is ColoredPetriNetValueKind.REAL:
        assert type(value.value) is float
        return value.value.hex()
    if value.kind is ColoredPetriNetValueKind.INTEGER:
        return str(value.value)
    if value.kind is ColoredPetriNetValueKind.STRING_SEQUENCE:
        assert type(value.value) is tuple
        return list(value.value)
    return value.value


def _represented_state(value: object) -> object:
    """Return canonical state for exact in-memory represented-input identity."""
    if value is None or type(value) in (bool, str):
        return value
    if type(value) is int:
        return str(value)
    if type(value) is float:
        return value.hex()
    if isinstance(value, StrEnum):
        return {"enum": type(value).__name__, "value": value.value}
    if type(value) is tuple:
        return [_represented_state(item) for item in value]
    if is_dataclass(value) and not isinstance(value, type):
        return {
            "type": type(value).__name__,
            "fields": [
                [item.name, _represented_state(getattr(value, item.name))]
                for item in fields(value)
            ],
        }
    raise TypeError(f"unsupported represented state type: {type(value).__name__}")


def _result_identity(
    definition: ColoredPetriNetDefinition,
    marking: ColoredPetriNetMarking,
    expression_identity: ColoredPetriNetExpressionEvaluatorIdentity,
    ordering_identity: ColoredPetriNetOrderingPolicyIdentity,
    enabler_identity: ColoredPetriNetTransitionEnablerIdentity,
    bindings: tuple[ColoredPetriNetBinding, ...] | None,
    failure: tuple[object, ...] | None,
) -> ColoredPetriNetEnablementResultIdentity:
    """Derive an identity closed over exact represented inputs and outcome."""
    encoded_bindings = None
    if bindings is not None:
        encoded_bindings = [
            {
                "transition": binding.transition_identity.value,
                "assignments": [
                    {
                        "variable": assignment.variable_identity.value,
                        "kind": assignment.value.kind.value,
                        "value": _identity_value(assignment.value),
                    }
                    for assignment in binding.assignments
                ],
            }
            for binding in bindings
        ]
    payload = {
        "domain": "ksdft2effmass.petrinet.colored.enablement-result-identity-v1",
        "definition": _represented_state(definition),
        "selection_policy": definition.selection_policy.value,
        "marking": _represented_state(marking),
        "expression": expression_identity.value,
        "ordering": ordering_identity.value,
        "enabler": enabler_identity.value,
        "bindings": encoded_bindings,
        "failure": failure,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return ColoredPetriNetEnablementResultIdentity(sha256(encoded).hexdigest())


@final
class ColoredPetriNetTransitionEnabler:
    """ActionObject enumerating the complete enabled transition/binding set."""

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Reject subclass-injected enablement policy."""
        raise TypeError("ColoredPetriNetTransitionEnabler does not support subclasses")

    def execute(
        self,
        definition: ColoredPetriNetDefinition,
        marking: ColoredPetriNetMarking,
        expression_evaluator_identity: ColoredPetriNetExpressionEvaluatorIdentity = (
            _EXPRESSION_EVALUATOR_IDENTITY
        ),
        ordering_policy_identity: ColoredPetriNetOrderingPolicyIdentity = (
            _ORDERING_POLICY_IDENTITY
        ),
    ) -> ColoredPetriNetEnablementResult:
        """Return complete deterministic enablement or one structured failure.

        Wrong public argument types raise ``TypeError``. Cross-object defects,
        unsupported semantic versions, and guard failures are represented by the
        returned closed failure variant.
        """
        expected = (
            (definition, ColoredPetriNetDefinition, "definition"),
            (marking, ColoredPetriNetMarking, "marking"),
            (
                expression_evaluator_identity,
                ColoredPetriNetExpressionEvaluatorIdentity,
                "expression_evaluator_identity",
            ),
            (
                ordering_policy_identity,
                ColoredPetriNetOrderingPolicyIdentity,
                "ordering_policy_identity",
            ),
        )
        for value, nominal_type, name in expected:
            if type(value) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        common = (
            definition,
            marking,
            expression_evaluator_identity,
            ordering_policy_identity,
            _TRANSITION_ENABLER_IDENTITY,
        )
        definition_validation = ColoredPetriNetDefinitionValidator().execute(definition)
        if not definition_validation.is_valid:
            return self._failure_result(
                common,
                ColoredPetriNetEnablementFailureCode.INVALID_DEFINITION,
                "definition_validation",
                "a structurally valid colored Petri-net definition",
                "definition validation returned findings",
                "enablement was not evaluated",
                definition_validation.issues,
            )
        marking_validation = ColoredPetriNetMarkingValidator().execute(
            definition, marking
        )
        if not marking_validation.is_valid:
            return self._failure_result(
                common,
                ColoredPetriNetEnablementFailureCode.INVALID_MARKING,
                "marking_validation",
                "a complete marking compatible with the exact definition",
                "marking validation returned findings",
                "enablement was not evaluated",
                marking_validation.issues,
            )
        if expression_evaluator_identity != _EXPRESSION_EVALUATOR_IDENTITY:
            return self._unsupported(
                common,
                ColoredPetriNetEnablementFailureCode.UNSUPPORTED_EXPRESSION_EVALUATOR,
                "expression_evaluator_resolution",
                _EXPRESSION_EVALUATOR_IDENTITY.value,
                expression_evaluator_identity.value,
            )
        if ordering_policy_identity != _ORDERING_POLICY_IDENTITY:
            return self._unsupported(
                common,
                ColoredPetriNetEnablementFailureCode.UNSUPPORTED_ORDERING_POLICY,
                "ordering_policy_resolution",
                _ORDERING_POLICY_IDENTITY.value,
                ordering_policy_identity.value,
            )

        priority = {
            identity: position
            for position, identity in enumerate(definition.transition_priority)
        }
        enabled: set[ColoredPetriNetBinding] = set()
        by_place = {place.place_identity: place.tokens for place in marking.places}
        evaluator = ColoredPetriNetExpressionEvaluator()
        for transition in definition.transitions:
            arcs = tuple(
                arc
                for arc in definition.arcs
                if arc.transition_identity == transition.identity
                and arc.input_inscription is not None
            )
            inhibited = False
            demands: list[
                tuple[object, ColoredPetriNetInputMode, ColoredPetriNetTokenPattern]
            ] = []
            candidates: list[tuple[tuple[int, ColoredPetriNetToken], ...]] = []
            for arc in arcs:
                inscription = arc.input_inscription
                assert inscription is not None
                tokens = by_place[arc.place_identity]
                if inscription.mode is ColoredPetriNetInputMode.INHIBIT:
                    for pattern in inscription.patterns:
                        if any(
                            token.color_identity in pattern.allowed_color_identities
                            for token in tokens
                        ):
                            inhibited = True
                            break
                    if inhibited:
                        break
                    continue
                for pattern in inscription.patterns:
                    assert type(pattern) is ColoredPetriNetTokenPattern
                    demands.append((arc.place_identity, inscription.mode, pattern))
                    candidates.append(
                        tuple(
                            (index, token)
                            for index, token in enumerate(tokens)
                            if token.color_identity in pattern.allowed_color_identities
                        )
                    )
            if inhibited or any(not items for items in candidates):
                continue
            choices = product(*candidates) if candidates else [()]
            for selected in choices:
                reserved: set[tuple[object, ColoredPetriNetInputMode, int]] = set()
                feasible = True
                values: dict[object, ColoredPetriNetValue] = {}
                for (place, mode, pattern), (index, token) in zip(
                    demands, selected, strict=True
                ):
                    key = (place, mode, index)
                    if key in reserved:
                        feasible = False
                        break
                    reserved.add(key)
                    values[pattern.variable_identity] = token.value
                if not feasible:
                    continue
                binding = ColoredPetriNetBinding(
                    transition.identity,
                    tuple(
                        ColoredPetriNetBindingAssignment(variable, values[variable])
                        for variable in transition.input_variable_identities
                    ),
                )
                try:
                    guard_value = evaluator.evaluate_guard(
                        transition.guard, binding
                    ).value
                except TypeError as exc:
                    return self._failure_result(
                        common,
                        ColoredPetriNetEnablementFailureCode.GUARD_EVALUATION_FAILED,
                        "guard_evaluation",
                        "a total well-typed guard for every feasible binding",
                        f"guard failed for transition {transition.identity.value}",
                        f"{type(exc).__name__}: {exc}",
                    )
                if guard_value:
                    enabled.add(binding)
        ordered = tuple(
            sorted(
                enabled,
                key=lambda binding: (
                    priority[binding.transition_identity],
                    tuple(_value_key(item.value) for item in binding.assignments),
                ),
            )
        )
        identity = _result_identity(*common, ordered, None)
        return ColoredPetriNetEnablementResult(
            identity,
            definition.identity,
            definition.selection_policy,
            marking.identity,
            expression_evaluator_identity,
            ordering_policy_identity,
            _TRANSITION_ENABLER_IDENTITY,
            enabled_bindings=ordered,
        )

    @staticmethod
    def _failure_result(
        common: tuple[
            ColoredPetriNetDefinition,
            ColoredPetriNetMarking,
            ColoredPetriNetExpressionEvaluatorIdentity,
            ColoredPetriNetOrderingPolicyIdentity,
            ColoredPetriNetTransitionEnablerIdentity,
        ],
        code: ColoredPetriNetEnablementFailureCode,
        phase: str,
        expected: str,
        observed: str,
        diagnostic: str,
        issues: tuple[ColoredPetriNetValidationIssue, ...] = (),
    ) -> ColoredPetriNetEnablementResult:
        """Build one identity-bound closed failure result."""
        issue_state = tuple(
            (issue.path, issue.code.value, issue.related_identities, issue.message)
            for issue in issues
        )
        failure_state: tuple[object, ...] = (
            code.value,
            phase,
            expected,
            observed,
            diagnostic,
            issue_state,
        )
        result_identity = _result_identity(*common, None, failure_state)
        failure = ColoredPetriNetEnablementFailure(
            ColoredPetriNetEnablementFailureIdentity(result_identity),
            code,
            phase,
            expected,
            observed,
            diagnostic,
            issues,
        )
        (
            definition,
            marking,
            expression_identity,
            ordering_identity,
            enabler_identity,
        ) = common
        return ColoredPetriNetEnablementResult(
            result_identity,
            definition.identity,
            definition.selection_policy,
            marking.identity,
            expression_identity,
            ordering_identity,
            enabler_identity,
            failure=failure,
        )

    @classmethod
    def _unsupported(
        cls,
        common: tuple[
            ColoredPetriNetDefinition,
            ColoredPetriNetMarking,
            ColoredPetriNetExpressionEvaluatorIdentity,
            ColoredPetriNetOrderingPolicyIdentity,
            ColoredPetriNetTransitionEnablerIdentity,
        ],
        code: ColoredPetriNetEnablementFailureCode,
        phase: str,
        expected: str,
        observed: str,
    ) -> ColoredPetriNetEnablementResult:
        """Return one unsupported-semantic-version failure."""
        return cls._failure_result(
            common,
            code,
            phase,
            expected,
            observed,
            "enablement was not evaluated under an unsupported semantic version",
        )
