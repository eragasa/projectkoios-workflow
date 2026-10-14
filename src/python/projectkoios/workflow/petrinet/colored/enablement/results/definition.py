"""Immutable enablement outcome vocabulary and embedded semantic identities."""

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from string import hexdigits
from ...definitions import CpnSelectionPolicy
from ...expressions.evaluation.expressions import CpnExpressionEvaluatorIdentity
from ...bindings import CpnBinding
from ...definitions import CpnDefinitionIdentity
from ...markings import CpnMarkingIdentity
from ...validation.findings import CpnValidationIssue


@dataclass(frozen=True, slots=True)
class CpnEnablementResultIdentity:
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
class CpnOrderingPolicyIdentity:
    """Nominal identity of exact enablement ordering semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError("ordering policy identity value must be a string")
        if not self.value:
            raise ValueError("ordering policy identity value must not be empty")


@dataclass(frozen=True, slots=True)
class CpnTransitionEnablerIdentity:
    """Nominal identity of exact transition-enablement semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError(
                "transition enabler identity value must be a string"
            )
        if not self.value:
            raise ValueError(
                "transition enabler identity value must not be empty"
            )


@dataclass(frozen=True, slots=True)
class CpnEnablementFailureIdentity:
    """Nominal identity of the failure variant of one enablement result."""

    result_identity: CpnEnablementResultIdentity

    def __post_init__(self) -> None:
        """Bind the failure identity to one exact result identity."""
        if type(self.result_identity) is not CpnEnablementResultIdentity:
            raise TypeError(
                "result_identity must be CpnEnablementResultIdentity"
            )


class CpnEnablementFailureCode(StrEnum):
    """Closed operational failure codes for complete enablement."""

    INVALID_DEFINITION = "invalid_definition"
    INVALID_MARKING = "invalid_marking"
    UNSUPPORTED_EXPRESSION_EVALUATOR = "unsupported_expression_evaluator"
    UNSUPPORTED_ORDERING_POLICY = "unsupported_ordering_policy"
    GUARD_EVALUATION_FAILED = "guard_evaluation_failed"


@dataclass(frozen=True, slots=True)
class CpnEnablementFailure:
    """One structured failure with no enabled-binding payload."""

    identity: CpnEnablementFailureIdentity
    code: CpnEnablementFailureCode
    operation_phase: str
    expected_condition: str
    observed_condition: str
    diagnostic: str
    validation_issues: tuple[CpnValidationIssue, ...] = ()
    claim_boundary: tuple[str, ...] = (
        "software enablement only",
        "no firing or external effect",
        "no scientific acceptance",
    )

    def __post_init__(self) -> None:
        """Validate immutable closed failure state."""
        if type(self.identity) is not CpnEnablementFailureIdentity:
            raise TypeError("identity must be CpnEnablementFailureIdentity")
        if not isinstance(self.code, CpnEnablementFailureCode):
            raise TypeError("code must be CpnEnablementFailureCode")
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
            type(item) is not CpnValidationIssue
            for item in self.validation_issues
        ):
            raise TypeError(
                "validation_issues must be a tuple of CpnValidationIssue"
            )
        if type(self.claim_boundary) is not tuple or any(
            type(item) is not str for item in self.claim_boundary
        ):
            raise TypeError("claim_boundary must be a tuple of strings")
        if not self.claim_boundary or any(
            not item for item in self.claim_boundary
        ):
            raise ValueError("claim_boundary must contain nonempty strings")


@dataclass(frozen=True, slots=True)
class CpnEnablementResult:
    """Closed complete success or failure for one definition and marking."""

    identity: CpnEnablementResultIdentity
    definition_identity: CpnDefinitionIdentity
    selection_policy: CpnSelectionPolicy
    marking_identity: CpnMarkingIdentity
    expression_evaluator_identity: CpnExpressionEvaluatorIdentity
    ordering_policy_identity: CpnOrderingPolicyIdentity
    transition_enabler_identity: CpnTransitionEnablerIdentity
    enabled_bindings: tuple[CpnBinding, ...] | None = None
    failure: CpnEnablementFailure | None = None

    def __post_init__(self) -> None:
        """Enforce exact nominal identities and one closed outcome variant."""
        expected = (
            ("identity", CpnEnablementResultIdentity),
            ("definition_identity", CpnDefinitionIdentity),
            ("selection_policy", CpnSelectionPolicy),
            ("marking_identity", CpnMarkingIdentity),
            (
                "expression_evaluator_identity",
                CpnExpressionEvaluatorIdentity,
            ),
            ("ordering_policy_identity", CpnOrderingPolicyIdentity),
            (
                "transition_enabler_identity",
                CpnTransitionEnablerIdentity,
            ),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        if self.enabled_bindings is not None and (
            type(self.enabled_bindings) is not tuple
            or any(
                type(item) is not CpnBinding for item in self.enabled_bindings
            )
        ):
            raise TypeError(
                "enabled_bindings must be a tuple of CpnBinding or None"
            )
        if self.failure is not None and (
            type(self.failure) is not CpnEnablementFailure
        ):
            raise TypeError("failure must be CpnEnablementFailure or None")
        if (self.enabled_bindings is None) == (self.failure is None):
            raise ValueError(
                "exactly one of enabled_bindings and failure must be present"
            )
        if self.enabled_bindings is not None and len(
            set(self.enabled_bindings)
        ) != len(self.enabled_bindings):
            raise ValueError("enabled_bindings must be unique")
        if self.failure is not None and (
            self.failure.identity.result_identity != self.identity
        ):
            raise ValueError("failure identity must bind this result identity")

    @property
    def is_success(self) -> bool:
        """Return whether this closed result contains enabled bindings."""
        return self.enabled_bindings is not None
