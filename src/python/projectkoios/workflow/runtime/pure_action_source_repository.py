"""Authoritative source lookup boundary for experimental pure-action inputs."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from string import hexdigits

from projectkoios.workflow.actions import (
    ExperimentalWorkflowInputSourceProfileIdentity,
)
from projectkoios.workflow.core.identities import stable_identity

from .pure_action_inputs import (
    ExperimentalWorkflowPureActionInputSourceEvidence,
)

_SOURCE_REFERENCE_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-source-reference:0"
)
_MAX_SOURCE_IDENTITY_BYTES = 512


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputSourceReferenceIdentity:
    """Content identity of one opaque immutable-source lookup key."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "input source reference identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputSourceRevisionIdentity:
    """Nominal content identity of one source-owner revision."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "input source revision identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputSourceReference:
    """Identify one exact source without carrying owner bytes or locators."""

    identity: ExperimentalWorkflowPureActionInputSourceReferenceIdentity = (
        field(init=False)
    )
    source_kind: str
    source_profile_identity: ExperimentalWorkflowInputSourceProfileIdentity
    source_identity: str

    def __post_init__(self) -> None:
        _validate_ascii_token(self.source_kind, "source kind")
        if type(self.source_profile_identity) is not (
            ExperimentalWorkflowInputSourceProfileIdentity
        ):
            raise TypeError(
                "source_profile_identity must be "
                "ExperimentalWorkflowInputSourceProfileIdentity"
            )
        profile = ExperimentalWorkflowInputSourceProfileIdentity(
            self.source_profile_identity.value
        )
        if profile != self.source_profile_identity:
            raise ValueError("source profile differs after validation")
        _validate_source_identity(self.source_identity)
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionInputSourceReferenceIdentity(
                stable_identity(
                    _SOURCE_REFERENCE_DOMAIN,
                    self.source_kind,
                    profile.value,
                    self.source_identity,
                )
            ),
        )


class ExperimentalWorkflowPureActionInputSourceLoadStatus(StrEnum):
    """Closed result of resolving one immutable owner/source record."""

    LOADED = "loaded"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputSourceLoadResult:
    """Closed source resolution result from an authoritative owner adapter."""

    status: ExperimentalWorkflowPureActionInputSourceLoadStatus
    reference: ExperimentalWorkflowPureActionInputSourceReference
    revision_identity: (
        ExperimentalWorkflowPureActionInputSourceRevisionIdentity | None
    )
    evidence: ExperimentalWorkflowPureActionInputSourceEvidence | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.status) is not (
            ExperimentalWorkflowPureActionInputSourceLoadStatus
        ):
            raise TypeError(
                "status must be "
                "ExperimentalWorkflowPureActionInputSourceLoadStatus"
            )
        reference = _reconstruct_reference(self.reference)
        _validate_diagnostics(self.diagnostics)
        if (
            self.status
            is ExperimentalWorkflowPureActionInputSourceLoadStatus.LOADED
        ):
            if type(self.revision_identity) is not (
                ExperimentalWorkflowPureActionInputSourceRevisionIdentity
            ):
                raise TypeError("loaded source requires revision identity")
            if type(self.evidence) is not (
                ExperimentalWorkflowPureActionInputSourceEvidence
            ):
                raise TypeError("loaded source requires source evidence")
            evidence = _reconstruct_evidence(self.evidence)
            if _reference_for(evidence) != reference:
                raise ValueError(
                    "loaded evidence differs from source reference"
                )
            if self.revision_identity.value != evidence.identity.value:
                raise ValueError(
                    "source revision differs from evidence identity"
                )
        elif self.revision_identity is not None or self.evidence is not None:
            raise ValueError("non-loaded source prohibits retained evidence")


class ExperimentalWorkflowPureActionInputSourceRepository(ABC):
    """Nominal owner-adapter boundary for immutable input-source resolution."""

    __slots__ = ()

    @abstractmethod
    def load(
        self,
        reference: ExperimentalWorkflowPureActionInputSourceReference,
    ) -> ExperimentalWorkflowPureActionInputSourceLoadResult:
        """Resolve one immutable source without exposing private locators."""


def _reference_for(
    evidence: ExperimentalWorkflowPureActionInputSourceEvidence,
) -> ExperimentalWorkflowPureActionInputSourceReference:
    return ExperimentalWorkflowPureActionInputSourceReference(
        source_kind=evidence.source_kind,
        source_profile_identity=evidence.source_profile_identity,
        source_identity=evidence.source_identity,
    )


def _reconstruct_reference(
    value: ExperimentalWorkflowPureActionInputSourceReference,
) -> ExperimentalWorkflowPureActionInputSourceReference:
    if type(value) is not ExperimentalWorkflowPureActionInputSourceReference:
        raise TypeError(
            "reference must be "
            "ExperimentalWorkflowPureActionInputSourceReference"
        )
    reconstructed = ExperimentalWorkflowPureActionInputSourceReference(
        source_kind=value.source_kind,
        source_profile_identity=value.source_profile_identity,
        source_identity=value.source_identity,
    )
    if reconstructed != value:
        raise ValueError("source reference differs after validation")
    return reconstructed


def _reconstruct_evidence(
    value: ExperimentalWorkflowPureActionInputSourceEvidence,
) -> ExperimentalWorkflowPureActionInputSourceEvidence:
    if type(value) is not ExperimentalWorkflowPureActionInputSourceEvidence:
        raise TypeError(
            "evidence must be ExperimentalWorkflowPureActionInputSourceEvidence"
        )
    reconstructed = ExperimentalWorkflowPureActionInputSourceEvidence(
        source_kind=value.source_kind,
        source_profile_identity=value.source_profile_identity,
        source_identity=value.source_identity,
        payload=value.payload,
    )
    if reconstructed != value:
        raise ValueError("source evidence differs after validation")
    return reconstructed


def _validate_ascii_token(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if not value or len(value) > 512 or value != value.strip():
        raise ValueError(f"{label} must be nonempty, bounded, and stripped")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError(f"{label} must contain ASCII only") from error
    if any(byte <= 0x20 or byte == 0x7F for byte in encoded):
        raise ValueError(f"{label} must exclude whitespace and controls")


def _validate_source_identity(value: str) -> None:
    _validate_ascii_token(value, "source identity")
    if len(value.encode("ascii")) > _MAX_SOURCE_IDENTITY_BYTES:
        raise ValueError("source identity exceeds its byte bound")
    lowered = value.lower()
    if (
        "/" in value
        or "\\" in value
        or value in {".", ".."}
        or value.startswith(("~", "./", "../"))
        or lowered.startswith("file:")
        or re.match(r"^[A-Za-z]:[\\/]", value) is not None
    ):
        raise ValueError("source identity must not be a machine path")


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


def _validate_diagnostics(values: tuple[str, ...]) -> None:
    if type(values) is not tuple:
        raise TypeError("diagnostics must be a tuple")
    if len(values) > 32:
        raise ValueError("diagnostics exceed their bound")
    if any(type(value) is not str or not value for value in values):
        raise TypeError("diagnostics must contain nonempty strings")


__all__ = [
    "ExperimentalWorkflowPureActionInputSourceLoadResult",
    "ExperimentalWorkflowPureActionInputSourceLoadStatus",
    "ExperimentalWorkflowPureActionInputSourceReference",
    "ExperimentalWorkflowPureActionInputSourceReferenceIdentity",
    "ExperimentalWorkflowPureActionInputSourceRepository",
    "ExperimentalWorkflowPureActionInputSourceRevisionIdentity",
]
