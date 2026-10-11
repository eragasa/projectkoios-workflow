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

from .canonical.bindings import (
    CpnCanonicalBindingCodec,
    CpnCanonicalBindingEncodingInput,
)
from .definitions import (
    CpnDefinition,
    CpnSelectionPolicy,
)
from .enablement import (
    CpnEnablementResult,
    CpnEnablementResultIdentity,
    CpnOrderingPolicyIdentity,
)
from .bindings import CpnBinding


@dataclass(frozen=True, slots=True)
class CpnSelectionDirectiveIdentity:
    """Content identity of one explicit selection directive."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact lowercase SHA-256 spelling."""
        if type(self.value) is not str:
            raise TypeError(
                "selection directive identity value must be a string"
            )
        if (
            len(self.value) != 64
            or self.value != self.value.lower()
            or any(character not in hexdigits for character in self.value)
        ):
            raise ValueError(
                "selection directive identity must be a lowercase SHA-256 digest"
            )


@dataclass(frozen=True, slots=True)
class CpnSelectionResultIdentity:
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
class CpnBindingSelectorIdentity:
    """Nominal identity of exact binding-selection semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError("binding selector identity value must be a string")
        if not self.value:
            raise ValueError(
                "binding selector identity value must not be empty"
            )


@dataclass(frozen=True, slots=True)
class CpnSelectionDirective:
    """Explicit request for one binding from one exact enablement result."""

    enablement_result_identity: CpnEnablementResultIdentity
    binding: CpnBinding
    identity: CpnSelectionDirectiveIdentity = field(init=False)

    def __post_init__(self) -> None:
        """Validate exact fields and derive the content identity."""
        if type(self.enablement_result_identity) is not (
            CpnEnablementResultIdentity
        ):
            raise TypeError(
                "enablement_result_identity must be CpnEnablementResultIdentity"
            )
        if type(self.binding) is not CpnBinding:
            raise TypeError("binding must be CpnBinding")
        binding_document = CpnCanonicalBindingCodec().encode(
            CpnCanonicalBindingEncodingInput(self.binding)
        )
        encoded = json.dumps(
            {
                "domain": "projectkoios.workflow.cpn.selection-directive:0.1",
                "enablement_result": self.enablement_result_identity.value,
                "binding_canonical_bytes_hex": (
                    binding_document.canonical_bytes.hex()
                ),
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        identity = CpnSelectionDirectiveIdentity(sha256(encoded).hexdigest())
        object.__setattr__(self, "identity", identity)


class CpnSelectionOutcomeKind(StrEnum):
    """Closed selection-result outcome variants."""

    SELECTED = "selected"
    EMPTY = "empty"
    NO_MATCH = "no_match"
    FAILURE = "failure"


class CpnSelectionFailureCode(StrEnum):
    """Closed selection failure codes."""

    ENABLEMENT_FAILED = "enablement_failed"
    DEFINITION_MISMATCH = "definition_mismatch"
    DIRECTED_SELECTION_PROHIBITED = "directed_selection_prohibited"
    DIRECTIVE_ENABLEMENT_MISMATCH = "directive_enablement_mismatch"


@dataclass(frozen=True, slots=True)
class CpnSelectionResult:
    """One identity-bound selected, empty, no-match, or failure outcome."""

    enablement_result_identity: CpnEnablementResultIdentity
    selector_identity: CpnBindingSelectorIdentity
    ordering_policy_identity: CpnOrderingPolicyIdentity
    outcome: CpnSelectionOutcomeKind
    selected_binding: CpnBinding | None = None
    directive: CpnSelectionDirective | None = None
    failure_code: CpnSelectionFailureCode | None = None
    identity: CpnSelectionResultIdentity = field(init=False)

    def __post_init__(self) -> None:
        """Enforce one closed outcome and derive its complete content identity."""
        expected = (
            (
                "enablement_result_identity",
                CpnEnablementResultIdentity,
            ),
            ("selector_identity", CpnBindingSelectorIdentity),
            ("ordering_policy_identity", CpnOrderingPolicyIdentity),
            ("outcome", CpnSelectionOutcomeKind),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        if self.selected_binding is not None and (
            type(self.selected_binding) is not CpnBinding
        ):
            raise TypeError("selected_binding must be CpnBinding or None")
        if self.directive is not None and (
            type(self.directive) is not CpnSelectionDirective
        ):
            raise TypeError("directive must be CpnSelectionDirective or None")
        if self.failure_code is not None and (
            not isinstance(self.failure_code, CpnSelectionFailureCode)
        ):
            raise TypeError(
                "failure_code must be CpnSelectionFailureCode or None"
            )
        valid = {
            CpnSelectionOutcomeKind.SELECTED: (
                self.selected_binding is not None and self.failure_code is None
            ),
            CpnSelectionOutcomeKind.EMPTY: (
                self.selected_binding is None
                and self.directive is None
                and self.failure_code is None
            ),
            CpnSelectionOutcomeKind.NO_MATCH: (
                self.selected_binding is None
                and self.directive is not None
                and self.failure_code is None
            ),
            CpnSelectionOutcomeKind.FAILURE: (
                self.selected_binding is None and self.failure_code is not None
            ),
        }[self.outcome]
        if not valid:
            raise ValueError(
                "selection fields do not match the outcome variant"
            )
        if self.outcome is CpnSelectionOutcomeKind.SELECTED and (
            self.directive is not None
            and (
                self.directive.enablement_result_identity
                != self.enablement_result_identity
                or self.directive.binding != self.selected_binding
            )
        ):
            raise ValueError(
                "selected directed result must match its exact directive"
            )
        if self.outcome is CpnSelectionOutcomeKind.NO_MATCH and (
            self.directive is None
            or self.directive.enablement_result_identity
            != self.enablement_result_identity
        ):
            raise ValueError(
                "no-match result requires a current exact directive"
            )
        binding_document = (
            None
            if self.selected_binding is None
            else CpnCanonicalBindingCodec().encode(
                CpnCanonicalBindingEncodingInput(self.selected_binding)
            )
        )
        encoded = json.dumps(
            {
                "domain": "projectkoios.workflow.cpn.selection-result:0.1",
                "enablement_result": self.enablement_result_identity.value,
                "selector": self.selector_identity.value,
                "ordering": self.ordering_policy_identity.value,
                "outcome": self.outcome.value,
                "binding_canonical_bytes_hex": (
                    None
                    if binding_document is None
                    else binding_document.canonical_bytes.hex()
                ),
                "directive": (
                    None
                    if self.directive is None
                    else self.directive.identity.value
                ),
                "failure": (
                    None
                    if self.failure_code is None
                    else self.failure_code.value
                ),
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        identity = CpnSelectionResultIdentity(sha256(encoded).hexdigest())
        object.__setattr__(self, "identity", identity)

    @property
    def directive_identity(
        self,
    ) -> CpnSelectionDirectiveIdentity | None:
        """Return the retained directive identity or explicit absence."""
        return None if self.directive is None else self.directive.identity


_SELECTOR_IDENTITY = CpnBindingSelectorIdentity(
    "colored-petri-net-binding-selector-v1"
)


@dataclass(frozen=True, slots=True)
class CpnBindingSelectionRequest:
    """Complete immutable request for deterministic or directed selection."""

    definition: CpnDefinition
    enablement: CpnEnablementResult
    directive: CpnSelectionDirective | None = None

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.enablement) is not CpnEnablementResult:
            raise TypeError("enablement must be CpnEnablementResult")
        if (
            self.directive is not None
            and type(self.directive) is not CpnSelectionDirective
        ):
            raise TypeError("directive must be CpnSelectionDirective or None")


@final
class CpnBindingSelector:
    """ActionObject selecting canonically or by one permitted directive."""

    __slots__ = ()

    @property
    def identity(self) -> CpnBindingSelectorIdentity:
        """Return exact binding-selection semantics identity."""
        return _SELECTOR_IDENTITY

    def execute(
        self, request: CpnBindingSelectionRequest
    ) -> CpnSelectionResult:
        """Return one closed deterministic selection outcome."""
        if type(request) is not CpnBindingSelectionRequest:
            raise TypeError("request must be CpnBindingSelectionRequest")
        definition = request.definition
        enablement = request.enablement
        directive = request.directive
        common: tuple[
            CpnEnablementResultIdentity,
            CpnBindingSelectorIdentity,
            CpnOrderingPolicyIdentity,
        ] = (
            enablement.identity,
            _SELECTOR_IDENTITY,
            enablement.ordering_policy_identity,
        )
        if (
            definition.identity != enablement.definition_identity
            or definition.selection_policy is not enablement.selection_policy
        ):
            return CpnSelectionResult(
                *common,
                CpnSelectionOutcomeKind.FAILURE,
                directive=directive,
                failure_code=CpnSelectionFailureCode.DEFINITION_MISMATCH,
            )
        if not enablement.is_success:
            return CpnSelectionResult(
                *common,
                CpnSelectionOutcomeKind.FAILURE,
                directive=directive,
                failure_code=CpnSelectionFailureCode.ENABLEMENT_FAILED,
            )
        assert enablement.enabled_bindings is not None
        if directive is None:
            if not enablement.enabled_bindings:
                return CpnSelectionResult(
                    *common, CpnSelectionOutcomeKind.EMPTY
                )
            return CpnSelectionResult(
                *common,
                CpnSelectionOutcomeKind.SELECTED,
                selected_binding=enablement.enabled_bindings[0],
            )
        if definition.selection_policy is not (
            CpnSelectionPolicy.DIRECTED_ALLOWED
        ):
            return CpnSelectionResult(
                *common,
                CpnSelectionOutcomeKind.FAILURE,
                directive=directive,
                failure_code=(
                    CpnSelectionFailureCode.DIRECTED_SELECTION_PROHIBITED
                ),
            )
        if directive.enablement_result_identity != enablement.identity:
            return CpnSelectionResult(
                *common,
                CpnSelectionOutcomeKind.FAILURE,
                directive=directive,
                failure_code=(
                    CpnSelectionFailureCode.DIRECTIVE_ENABLEMENT_MISMATCH
                ),
            )
        if directive.binding not in enablement.enabled_bindings:
            return CpnSelectionResult(
                *common,
                CpnSelectionOutcomeKind.NO_MATCH,
                directive=directive,
            )
        return CpnSelectionResult(
            *common,
            CpnSelectionOutcomeKind.SELECTED,
            selected_binding=directive.binding,
            directive=directive,
        )
