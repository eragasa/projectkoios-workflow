"""Exact-byte verification for retained owner-payload references."""

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import final

from ..bindings import WorkflowPayloadColorBinding
from .definition import WorkflowDomainPayloadReference


class WorkflowDomainPayloadReferenceVerificationIssueCode(StrEnum):
    """Closed payload-reference correlation failures."""

    PAYLOAD_TOO_LARGE = "payload_too_large"
    BYTE_SIZE_MISMATCH = "byte_size_mismatch"
    SHA256_MISMATCH = "sha256_mismatch"
    SCHEMA_MISMATCH = "schema_mismatch"
    MEDIA_TYPE_MISMATCH = "media_type_mismatch"


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceVerificationIssue:
    """One deterministic exact-byte or compiled-binding mismatch."""

    code: WorkflowDomainPayloadReferenceVerificationIssueCode
    path: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.code,
            WorkflowDomainPayloadReferenceVerificationIssueCode,
        ):
            raise TypeError("code has the wrong type")
        if type(self.path) is not tuple or any(
            type(item) is not str or not item for item in self.path
        ):
            raise TypeError("path must contain nonempty strings")


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceVerificationRequest:
    """Retained reference, supplied bytes, and exact compiled color binding."""

    reference: WorkflowDomainPayloadReference
    payload_bytes: bytes
    color_binding: WorkflowPayloadColorBinding

    def __post_init__(self) -> None:
        if type(self.reference) is not WorkflowDomainPayloadReference:
            raise TypeError("reference must be WorkflowDomainPayloadReference")
        if type(self.payload_bytes) is not bytes:
            raise TypeError("payload_bytes must be bytes")
        if type(self.color_binding) is not WorkflowPayloadColorBinding:
            raise TypeError("color_binding must be WorkflowPayloadColorBinding")


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceVerificationResult:
    """Complete ordered reference-correlation findings."""

    issues: tuple[WorkflowDomainPayloadReferenceVerificationIssue, ...]

    def __post_init__(self) -> None:
        if type(self.issues) is not tuple or any(
            type(item) is not WorkflowDomainPayloadReferenceVerificationIssue
            for item in self.issues
        ):
            raise TypeError("issues must contain exact verification issues")
        if len(set(self.issues)) != len(self.issues):
            raise ValueError("issues must be unique")

    @property
    def is_verified(self) -> bool:
        """Return whether exact bytes and compiled binding agree."""
        return not self.issues


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceVerifierIdentity:
    """Identity of exact retained payload byte-correlation semantics."""

    value: str = "projectkoios.workflow.payload-reference-verifier:1"


@final
class WorkflowDomainPayloadReferenceVerifier:
    """Verify bytes and binding without owner decoding or artifact resolution."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowDomainPayloadReferenceVerifierIdentity:
        """Return exact retained payload verification semantics identity."""
        return WorkflowDomainPayloadReferenceVerifierIdentity()

    def execute(
        self, request: WorkflowDomainPayloadReferenceVerificationRequest
    ) -> WorkflowDomainPayloadReferenceVerificationResult:
        """Return every deterministic exact-byte and binding mismatch."""
        if (
            type(request)
            is not WorkflowDomainPayloadReferenceVerificationRequest
        ):
            raise TypeError(
                "request must be WorkflowDomainPayloadReferenceVerificationRequest"
            )
        reference = request.reference
        binding = request.color_binding
        payload_bytes = request.payload_bytes
        issues: list[WorkflowDomainPayloadReferenceVerificationIssue] = []
        if len(payload_bytes) > binding.maximum_payload_bytes:
            issues.append(
                WorkflowDomainPayloadReferenceVerificationIssue(
                    WorkflowDomainPayloadReferenceVerificationIssueCode.PAYLOAD_TOO_LARGE,
                    ("payload_bytes",),
                )
            )
        if len(payload_bytes) != reference.byte_size:
            issues.append(
                WorkflowDomainPayloadReferenceVerificationIssue(
                    WorkflowDomainPayloadReferenceVerificationIssueCode.BYTE_SIZE_MISMATCH,
                    ("reference", "byte_size"),
                )
            )
        if sha256(payload_bytes).hexdigest() != reference.sha256:
            issues.append(
                WorkflowDomainPayloadReferenceVerificationIssue(
                    WorkflowDomainPayloadReferenceVerificationIssueCode.SHA256_MISMATCH,
                    ("reference", "sha256"),
                )
            )
        if reference.schema_identity != binding.payload_schema_identity:
            issues.append(
                WorkflowDomainPayloadReferenceVerificationIssue(
                    WorkflowDomainPayloadReferenceVerificationIssueCode.SCHEMA_MISMATCH,
                    ("reference", "schema_identity"),
                )
            )
        if reference.media_type != binding.media_type_identity:
            issues.append(
                WorkflowDomainPayloadReferenceVerificationIssue(
                    WorkflowDomainPayloadReferenceVerificationIssueCode.MEDIA_TYPE_MISMATCH,
                    ("reference", "media_type"),
                )
            )
        return WorkflowDomainPayloadReferenceVerificationResult(tuple(issues))
