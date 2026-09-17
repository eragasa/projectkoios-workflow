"""Deterministic and explicitly permitted directed binding selection.

Selection consumes one complete identity-bound enablement result. It performs no
firing, marking mutation, Task invocation, external effect, authority decision,
persistence, fairness scheduling, or scientific calculation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from string import hexdigits
from typing import final

from .definitions import ColoredPetriNetDefinition, ColoredPetriNetSelectionPolicy
from .enablement import (
    ColoredPetriNetEnablementResult,
    ColoredPetriNetEnablementResultIdentity,
    ColoredPetriNetOrderingPolicyIdentity,
)
from .markings import ColoredPetriNetBinding


def _digest(payload: dict[str, object]) -> str:
    """Return one domain-owned canonical SHA-256 digest."""
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _value_state(value: object) -> object:
    """Return one JSON-safe tagged-value active representation."""
    if type(value) is float:
        return value.hex()
    if type(value) is tuple:
        return list(value)
    if type(value) is int:
        return str(value)
    return value


def _binding_state(binding: ColoredPetriNetBinding) -> dict[str, object]:
    """Return the canonical semantic identity state for one binding."""
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


@dataclass(frozen=True, slots=True)
class ColoredPetriNetSelectionDirectiveIdentity:
    """Content identity of one explicit selection directive."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact lowercase SHA-256 spelling."""
        if type(self.value) is not str:
            raise TypeError("selection directive identity value must be a string")
        if (
            len(self.value) != 64
            or self.value != self.value.lower()
            or any(character not in hexdigits for character in self.value)
        ):
            raise ValueError(
                "selection directive identity must be a lowercase SHA-256 digest"
            )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetSelectionResultIdentity:
    """Content identity of one closed selection result."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact lowercase SHA-256 spelling."""
        if type(self.value) is not str:
            raise TypeError("selection result identity value must be a string")
        if (
            len(self.value) != 64
            or self.value != self.value.lower()
            or any(character not in hexdigits for character in self.value)
        ):
            raise ValueError(
                "selection result identity must be a lowercase SHA-256 digest"
            )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetBindingSelectorIdentity:
    """Nominal identity of exact binding-selection semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError("binding selector identity value must be a string")
        if not self.value:
            raise ValueError("binding selector identity value must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetSelectionDirective:
    """Explicit request for one binding from one exact enablement result."""

    enablement_result_identity: ColoredPetriNetEnablementResultIdentity
    binding: ColoredPetriNetBinding
    identity: ColoredPetriNetSelectionDirectiveIdentity = field(init=False)

    def __post_init__(self) -> None:
        """Validate exact fields and derive the content identity."""
        if type(self.enablement_result_identity) is not (
            ColoredPetriNetEnablementResultIdentity
        ):
            raise TypeError(
                "enablement_result_identity must be "
                "ColoredPetriNetEnablementResultIdentity"
            )
        if type(self.binding) is not ColoredPetriNetBinding:
            raise TypeError("binding must be ColoredPetriNetBinding")
        identity = ColoredPetriNetSelectionDirectiveIdentity(
            _digest(
                {
                    "domain": (
                        "ksdft2effmass.petrinet.colored.selection-directive-identity-v1"
                    ),
                    "enablement_result": self.enablement_result_identity.value,
                    "binding": _binding_state(self.binding),
                }
            )
        )
        object.__setattr__(self, "identity", identity)


class ColoredPetriNetSelectionOutcomeKind(StrEnum):
    """Closed selection-result outcome variants."""

    SELECTED = "selected"
    EMPTY = "empty"
    NO_MATCH = "no_match"
    FAILURE = "failure"


class ColoredPetriNetSelectionFailureCode(StrEnum):
    """Closed selection failure codes."""

    ENABLEMENT_FAILED = "enablement_failed"
    DEFINITION_MISMATCH = "definition_mismatch"
    DIRECTED_SELECTION_PROHIBITED = "directed_selection_prohibited"
    DIRECTIVE_ENABLEMENT_MISMATCH = "directive_enablement_mismatch"


@dataclass(frozen=True, slots=True)
class ColoredPetriNetSelectionResult:
    """One identity-bound selected, empty, no-match, or failure outcome."""

    enablement_result_identity: ColoredPetriNetEnablementResultIdentity
    selector_identity: ColoredPetriNetBindingSelectorIdentity
    ordering_policy_identity: ColoredPetriNetOrderingPolicyIdentity
    outcome: ColoredPetriNetSelectionOutcomeKind
    selected_binding: ColoredPetriNetBinding | None = None
    directive: ColoredPetriNetSelectionDirective | None = None
    failure_code: ColoredPetriNetSelectionFailureCode | None = None
    identity: ColoredPetriNetSelectionResultIdentity = field(init=False)

    def __post_init__(self) -> None:
        """Enforce one closed outcome and derive its complete content identity."""
        expected = (
            (
                "enablement_result_identity",
                ColoredPetriNetEnablementResultIdentity,
            ),
            ("selector_identity", ColoredPetriNetBindingSelectorIdentity),
            ("ordering_policy_identity", ColoredPetriNetOrderingPolicyIdentity),
            ("outcome", ColoredPetriNetSelectionOutcomeKind),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        if self.selected_binding is not None and (
            type(self.selected_binding) is not ColoredPetriNetBinding
        ):
            raise TypeError("selected_binding must be ColoredPetriNetBinding or None")
        if self.directive is not None and (
            type(self.directive) is not ColoredPetriNetSelectionDirective
        ):
            raise TypeError(
                "directive must be ColoredPetriNetSelectionDirective or None"
            )
        if self.failure_code is not None and (
            not isinstance(self.failure_code, ColoredPetriNetSelectionFailureCode)
        ):
            raise TypeError(
                "failure_code must be ColoredPetriNetSelectionFailureCode or None"
            )
        valid = {
            ColoredPetriNetSelectionOutcomeKind.SELECTED: (
                self.selected_binding is not None and self.failure_code is None
            ),
            ColoredPetriNetSelectionOutcomeKind.EMPTY: (
                self.selected_binding is None
                and self.directive is None
                and self.failure_code is None
            ),
            ColoredPetriNetSelectionOutcomeKind.NO_MATCH: (
                self.selected_binding is None
                and self.directive is not None
                and self.failure_code is None
            ),
            ColoredPetriNetSelectionOutcomeKind.FAILURE: (
                self.selected_binding is None and self.failure_code is not None
            ),
        }[self.outcome]
        if not valid:
            raise ValueError("selection fields do not match the outcome variant")
        if self.outcome is ColoredPetriNetSelectionOutcomeKind.SELECTED and (
            self.directive is not None
            and (
                self.directive.enablement_result_identity
                != self.enablement_result_identity
                or self.directive.binding != self.selected_binding
            )
        ):
            raise ValueError("selected directed result must match its exact directive")
        if self.outcome is ColoredPetriNetSelectionOutcomeKind.NO_MATCH and (
            self.directive is None
            or self.directive.enablement_result_identity
            != self.enablement_result_identity
        ):
            raise ValueError("no-match result requires a current exact directive")
        identity = ColoredPetriNetSelectionResultIdentity(
            _digest(
                {
                    "domain": (
                        "ksdft2effmass.petrinet.colored.selection-result-identity-v1"
                    ),
                    "enablement_result": self.enablement_result_identity.value,
                    "selector": self.selector_identity.value,
                    "ordering": self.ordering_policy_identity.value,
                    "outcome": self.outcome.value,
                    "binding": (
                        None
                        if self.selected_binding is None
                        else _binding_state(self.selected_binding)
                    ),
                    "directive": (
                        None
                        if self.directive is None
                        else self.directive.identity.value
                    ),
                    "failure": (
                        None if self.failure_code is None else self.failure_code.value
                    ),
                }
            )
        )
        object.__setattr__(self, "identity", identity)

    @property
    def directive_identity(self) -> ColoredPetriNetSelectionDirectiveIdentity | None:
        """Return the retained directive identity or explicit absence."""
        return None if self.directive is None else self.directive.identity


_SELECTOR_IDENTITY = ColoredPetriNetBindingSelectorIdentity(
    "colored-petri-net-binding-selector-v1"
)


@final
class ColoredPetriNetBindingSelector:
    """ActionObject selecting canonically or by one permitted directive."""

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Reject subclass-injected selection policy."""
        raise TypeError("ColoredPetriNetBindingSelector does not support subclasses")

    def execute(
        self,
        definition: ColoredPetriNetDefinition,
        enablement: ColoredPetriNetEnablementResult,
        directive: ColoredPetriNetSelectionDirective | None = None,
    ) -> ColoredPetriNetSelectionResult:
        """Return one closed deterministic selection outcome."""
        if type(definition) is not ColoredPetriNetDefinition:
            raise TypeError("definition must be ColoredPetriNetDefinition")
        if type(enablement) is not ColoredPetriNetEnablementResult:
            raise TypeError("enablement must be ColoredPetriNetEnablementResult")
        if (
            directive is not None
            and type(directive) is not ColoredPetriNetSelectionDirective
        ):
            raise TypeError(
                "directive must be ColoredPetriNetSelectionDirective or None"
            )
        common: tuple[
            ColoredPetriNetEnablementResultIdentity,
            ColoredPetriNetBindingSelectorIdentity,
            ColoredPetriNetOrderingPolicyIdentity,
        ] = (
            enablement.identity,
            _SELECTOR_IDENTITY,
            enablement.ordering_policy_identity,
        )
        if (
            definition.identity != enablement.definition_identity
            or definition.selection_policy is not enablement.selection_policy
        ):
            return ColoredPetriNetSelectionResult(
                *common,
                ColoredPetriNetSelectionOutcomeKind.FAILURE,
                directive=directive,
                failure_code=ColoredPetriNetSelectionFailureCode.DEFINITION_MISMATCH,
            )
        if not enablement.is_success:
            return ColoredPetriNetSelectionResult(
                *common,
                ColoredPetriNetSelectionOutcomeKind.FAILURE,
                directive=directive,
                failure_code=ColoredPetriNetSelectionFailureCode.ENABLEMENT_FAILED,
            )
        assert enablement.enabled_bindings is not None
        if directive is None:
            if not enablement.enabled_bindings:
                return ColoredPetriNetSelectionResult(
                    *common, ColoredPetriNetSelectionOutcomeKind.EMPTY
                )
            return ColoredPetriNetSelectionResult(
                *common,
                ColoredPetriNetSelectionOutcomeKind.SELECTED,
                selected_binding=enablement.enabled_bindings[0],
            )
        if definition.selection_policy is not (
            ColoredPetriNetSelectionPolicy.DIRECTED_ALLOWED
        ):
            return ColoredPetriNetSelectionResult(
                *common,
                ColoredPetriNetSelectionOutcomeKind.FAILURE,
                directive=directive,
                failure_code=(
                    ColoredPetriNetSelectionFailureCode.DIRECTED_SELECTION_PROHIBITED
                ),
            )
        if directive.enablement_result_identity != enablement.identity:
            return ColoredPetriNetSelectionResult(
                *common,
                ColoredPetriNetSelectionOutcomeKind.FAILURE,
                directive=directive,
                failure_code=(
                    ColoredPetriNetSelectionFailureCode.DIRECTIVE_ENABLEMENT_MISMATCH
                ),
            )
        if directive.binding not in enablement.enabled_bindings:
            return ColoredPetriNetSelectionResult(
                *common,
                ColoredPetriNetSelectionOutcomeKind.NO_MATCH,
                directive=directive,
            )
        return ColoredPetriNetSelectionResult(
            *common,
            ColoredPetriNetSelectionOutcomeKind.SELECTED,
            selected_binding=directive.binding,
            directive=directive,
        )
