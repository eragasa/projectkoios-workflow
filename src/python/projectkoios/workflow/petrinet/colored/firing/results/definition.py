"""Identity-bound success and failure outcomes for pure firing."""

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from string import hexdigits
from ...markings import CpnMarking
from ...validation.findings import CpnValidationIssue
from ..audits import CpnFiringAudit
from ..inputs import CpnFiringInput


@dataclass(frozen=True, slots=True)
class CpnFiringResultIdentity:
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


class CpnFiringFailureCode(StrEnum):
    """Closed pure-firing failure codes."""

    INVALID_DEFINITION = "invalid_definition"
    INVALID_PREDECESSOR_MARKING = "invalid_predecessor_marking"
    ENABLEMENT_MISMATCH = "enablement_mismatch"
    SELECTION_MISMATCH = "selection_mismatch"
    DIRECTIVE_MISMATCH = "directive_mismatch"
    TRANSITION_OR_BINDING_MISMATCH = "transition_or_binding_mismatch"
    EXTERNAL_OUTPUT_BINDING_MISMATCH = "external_output_binding_mismatch"
    INPUT_OCCURRENCE_RECONSTRUCTION_FAILED = (
        "input_occurrence_reconstruction_failed"
    )
    OUTPUT_EVALUATION_FAILED = "output_evaluation_failed"
    PRODUCED_TOKEN_INVALID = "produced_token_invalid"
    TOKEN_IDENTITY_COLLISION = "token_identity_collision"


@dataclass(frozen=True, slots=True)
class CpnFiringFailureIdentity:
    """Nominal identity of the failure variant of one firing result."""

    result_identity: CpnFiringResultIdentity

    def __post_init__(self) -> None:
        """Bind to one exact firing-result identity."""
        if type(self.result_identity) is not CpnFiringResultIdentity:
            raise TypeError("result_identity must be CpnFiringResultIdentity")


@dataclass(frozen=True, slots=True)
class CpnFiringFailure:
    """Structured pure-firing failure with no successor."""

    identity: CpnFiringFailureIdentity
    code: CpnFiringFailureCode
    operation_phase: str
    expected_condition: str
    observed_condition: str
    diagnostic: str
    validation_issues: tuple[CpnValidationIssue, ...] = ()
    claim_boundary: tuple[str, ...] = (
        "pure generic firing only",
        "no external effect or authority",
        "no scientific acceptance",
    )

    def __post_init__(self) -> None:
        """Validate immutable structured failure state."""
        if type(self.identity) is not CpnFiringFailureIdentity:
            raise TypeError("identity must be CpnFiringFailureIdentity")
        if not isinstance(self.code, CpnFiringFailureCode):
            raise TypeError("code must be CpnFiringFailureCode")
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


class CpnFiringOutcomeKind(StrEnum):
    """Closed success or failure firing outcome."""

    SUCCESS = "success"
    FAILURE = "failure"


@dataclass(frozen=True, slots=True)
class CpnFiringResult:
    """One identity-bound pure-firing success or failure."""

    identity: CpnFiringResultIdentity
    firing_input: CpnFiringInput
    outcome: CpnFiringOutcomeKind
    successor_marking: CpnMarking | None = None
    audit: CpnFiringAudit | None = None
    failure: CpnFiringFailure | None = None

    def __post_init__(self) -> None:
        """Enforce exact nominal types and one closed outcome."""
        if type(self.identity) is not CpnFiringResultIdentity:
            raise TypeError("identity must be CpnFiringResultIdentity")
        if type(self.firing_input) is not CpnFiringInput:
            raise TypeError("firing_input must be CpnFiringInput")
        if not isinstance(self.outcome, CpnFiringOutcomeKind):
            raise TypeError("outcome must be CpnFiringOutcomeKind")
        valid = (
            self.outcome is CpnFiringOutcomeKind.SUCCESS
            and type(self.successor_marking) is CpnMarking
            and type(self.audit) is CpnFiringAudit
            and self.failure is None
        ) or (
            self.outcome is CpnFiringOutcomeKind.FAILURE
            and self.successor_marking is None
            and self.audit is None
            and type(self.failure) is CpnFiringFailure
        )
        if not valid:
            raise ValueError("firing fields do not match the outcome variant")
        if self.failure is not None and (
            self.failure.identity.result_identity != self.identity
        ):
            raise ValueError("failure identity must bind this result identity")
