"""Canonical firing-result documents and typed transport boundaries."""

from __future__ import annotations
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits
from ...firing.results import CpnFiringResult
from ...profiles.definition import WorkflowCpnExecutionProfile


_FIRING_PROFILE = "projectkoios.workflow.cpn-firing-result-json:0.1.0"


_MAXIMUM_FIRING_BYTES = 67_108_864


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResultIdentity:
    """Content-derived identity of exact canonical firing-result bytes."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity must be a string")
        prefix = "projectkoios.workflow.cpn-firing-result:0.1:"
        if not self.value.startswith(prefix):
            raise ValueError("identity has the wrong domain")
        digest = self.value.removeprefix(prefix)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError("identity must end in lowercase SHA-256")


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResult:
    """Exact firing-result bytes and constructor-derived correlations."""

    canonical_bytes: bytes
    representation_profile_identity: str = field(init=False)
    sha256: str = field(init=False)
    identity: CpnCanonicalFiringResultIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not self.canonical_bytes:
            raise ValueError("canonical_bytes must not be empty")
        if len(self.canonical_bytes) > _MAXIMUM_FIRING_BYTES:
            raise ValueError("canonical firing result exceeds byte bound")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self, "representation_profile_identity", _FIRING_PROFILE
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            CpnCanonicalFiringResultIdentity(
                "projectkoios.workflow.cpn-firing-result:0.1:" + digest
            ),
        )


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResultEncodingInput:
    """One exact pure result and the profile governing its replay."""

    result: CpnFiringResult
    execution_profile: WorkflowCpnExecutionProfile

    def __post_init__(self) -> None:
        if type(self.result) is not CpnFiringResult:
            raise TypeError("result must be CpnFiringResult")
        if type(self.execution_profile) is not WorkflowCpnExecutionProfile:
            raise TypeError(
                "execution_profile must be WorkflowCpnExecutionProfile"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResultDecodingInput:
    """Retained result and the exact retained replay profile."""

    canonical_result: CpnCanonicalFiringResult
    execution_profile: WorkflowCpnExecutionProfile

    def __post_init__(self) -> None:
        if type(self.canonical_result) is not CpnCanonicalFiringResult:
            raise TypeError("canonical_result must be CpnCanonicalFiringResult")
        if type(self.execution_profile) is not WorkflowCpnExecutionProfile:
            raise TypeError(
                "execution_profile must be WorkflowCpnExecutionProfile"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResultDecodingResult:
    """One pure firing result reconstructed by deterministic replay."""

    result: CpnFiringResult

    def __post_init__(self) -> None:
        if type(self.result) is not CpnFiringResult:
            raise TypeError("result must be CpnFiringResult")
