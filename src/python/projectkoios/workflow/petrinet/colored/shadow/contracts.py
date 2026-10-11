"""Immutable contracts for canonical shadow firing."""

from dataclasses import dataclass
from enum import StrEnum
from string import hexdigits

from ..canonical.definitions import (
    CpnCanonicalDefinition,
    CpnCanonicalDefinitionIdentity,
)
from ..canonical.markings import (
    CpnCanonicalMarking,
    CpnCanonicalMarkingIdentity,
)
from ..firing import (
    CpnFiringInput,
    CpnFiringOutcomeKind,
    CpnFiringResult,
    CpnFiringResultIdentity,
)
from ..profiles.definition import (
    WorkflowCpnExecutionProfile,
    WorkflowCpnExecutionProfileIdentity,
)

_SHADOW_RESULT_DOMAIN = "projectkoios.workflow.cpn-shadow-firing-result:0.1:"


class CpnShadowFiringErrorCode(StrEnum):
    """Closed shadow-admission and replay-correlation failures."""

    INVALID_ARGUMENT = "invalid_argument"
    DEFINITION_MISMATCH = "definition_mismatch"
    PREDECESSOR_MARKING_MISMATCH = "predecessor_marking_mismatch"
    EXECUTION_PROFILE_UNAVAILABLE = "execution_profile_unavailable"
    RETAINED_RESULT_MISMATCH = "retained_result_mismatch"


class CpnShadowFiringError(ValueError):
    """One inspectable closed shadow-firing failure."""

    def __init__(
        self,
        code: CpnShadowFiringErrorCode,
        path: tuple[str, ...],
        diagnostic: str,
    ) -> None:
        if not isinstance(code, CpnShadowFiringErrorCode):
            raise TypeError("code must be CpnShadowFiringErrorCode")
        if type(path) is not tuple or any(
            type(item) is not str for item in path
        ):
            raise TypeError("path must be a tuple of strings")
        if type(diagnostic) is not str or not diagnostic:
            raise TypeError("diagnostic must be a nonempty string")
        self.code = code
        self.path = path
        self.diagnostic = diagnostic
        super().__init__(
            f"{code.value} at {'.'.join(path) or '$'}: {diagnostic}"
        )


@dataclass(frozen=True, slots=True)
class CpnShadowFirerIdentity:
    """Identity of exact canonical shadow-firing semantics."""

    value: str = "projectkoios.workflow.cpn.shadow-firer:0.1"


@dataclass(frozen=True, slots=True)
class CpnShadowFiringResultIdentity:
    """Domain-separated content identity of one shadow result."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity value must be a string")
        if not self.value.startswith(_SHADOW_RESULT_DOMAIN):
            raise ValueError("shadow result identity has the wrong domain")
        digest = self.value.removeprefix(_SHADOW_RESULT_DOMAIN)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError(
                "shadow result identity must end in lowercase SHA-256"
            )


@dataclass(frozen=True, slots=True)
class CpnShadowFiringInput:
    """Canonical definition, profile, marking, and exact pure-firing input."""

    canonical_definition: CpnCanonicalDefinition
    execution_profile: WorkflowCpnExecutionProfile
    canonical_predecessor_marking: CpnCanonicalMarking
    firing_input: CpnFiringInput

    def __post_init__(self) -> None:
        expected = (
            ("canonical_definition", CpnCanonicalDefinition),
            ("execution_profile", WorkflowCpnExecutionProfile),
            ("canonical_predecessor_marking", CpnCanonicalMarking),
            ("firing_input", CpnFiringInput),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")


@dataclass(frozen=True, slots=True)
class CpnShadowFiringResult:
    """Complete definition/profile/marking/firing replay correlations."""

    identity: CpnShadowFiringResultIdentity
    canonical_definition_identity: CpnCanonicalDefinitionIdentity
    canonical_definition_sha256: str
    execution_profile_identity: WorkflowCpnExecutionProfileIdentity
    predecessor_marking_identity: CpnCanonicalMarkingIdentity
    predecessor_marking_sha256: str
    firing_result_identity: CpnFiringResultIdentity
    successor_marking_identity: CpnCanonicalMarkingIdentity | None
    successor_marking_sha256: str | None
    firing_result: CpnFiringResult

    def __post_init__(self) -> None:
        expected = (
            ("identity", CpnShadowFiringResultIdentity),
            ("canonical_definition_identity", CpnCanonicalDefinitionIdentity),
            ("execution_profile_identity", WorkflowCpnExecutionProfileIdentity),
            ("predecessor_marking_identity", CpnCanonicalMarkingIdentity),
            ("firing_result_identity", CpnFiringResultIdentity),
            ("firing_result", CpnFiringResult),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        for name in (
            "canonical_definition_sha256",
            "predecessor_marking_sha256",
        ):
            value = getattr(self, name)
            if not (
                type(value) is str
                and len(value) == 64
                and value == value.lower()
                and all(item in hexdigits for item in value)
            ):
                raise ValueError(f"{name} must be lowercase SHA-256")
        if self.firing_result_identity != self.firing_result.identity:
            raise ValueError("firing result identity correlation differs")
        is_success = self.firing_result.outcome is CpnFiringOutcomeKind.SUCCESS
        if is_success != (self.successor_marking_identity is not None):
            raise ValueError(
                "successor identity presence must match firing outcome"
            )
        if is_success != (self.successor_marking_sha256 is not None):
            raise ValueError(
                "successor digest presence must match firing outcome"
            )
        if self.successor_marking_sha256 is not None and not (
            len(self.successor_marking_sha256) == 64
            and self.successor_marking_sha256
            == self.successor_marking_sha256.lower()
            and all(item in hexdigits for item in self.successor_marking_sha256)
        ):
            raise ValueError(
                "successor_marking_sha256 must be lowercase SHA-256"
            )
