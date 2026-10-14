"""Pure assembly of retained payload references from owner bytes and metadata."""

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import final

from ..bindings import WorkflowPayloadColorBinding
from .definition import (
    WorkflowDomainPayloadEncodingMetadata,
    WorkflowDomainPayloadReference,
)


class WorkflowDomainPayloadReferenceAssemblyFailureCode(StrEnum):
    """Closed payload-reference assembly failures."""

    EMPTY_PAYLOAD = "empty_payload"
    PAYLOAD_TOO_LARGE = "payload_too_large"
    SCHEMA_MISMATCH = "schema_mismatch"
    MEDIA_TYPE_MISMATCH = "media_type_mismatch"
    INVALID_ARTIFACT_IDENTITY = "invalid_artifact_identity"


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceAssemblyFailure:
    """One inspectable failure before a reference can exist."""

    code: WorkflowDomainPayloadReferenceAssemblyFailureCode
    path: tuple[str, ...]
    diagnostic: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.code,
            WorkflowDomainPayloadReferenceAssemblyFailureCode,
        ):
            raise TypeError("code has the wrong type")
        if type(self.path) is not tuple or any(
            type(item) is not str or not item for item in self.path
        ):
            raise TypeError("path must contain nonempty strings")
        if type(self.diagnostic) is not str or not self.diagnostic:
            raise TypeError("diagnostic must be a nonempty string")


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceAssemblyRequest:
    """Exact owner bytes, metadata, store identity, and compiled binding."""

    payload_bytes: bytes
    encoding_metadata: WorkflowDomainPayloadEncodingMetadata
    artifact_identity: str
    color_binding: WorkflowPayloadColorBinding

    def __post_init__(self) -> None:
        if type(self.payload_bytes) is not bytes:
            raise TypeError("payload_bytes must be bytes")
        if (
            type(self.encoding_metadata)
            is not WorkflowDomainPayloadEncodingMetadata
        ):
            raise TypeError(
                "encoding_metadata must be WorkflowDomainPayloadEncodingMetadata"
            )
        if type(self.artifact_identity) is not str:
            raise TypeError("artifact_identity must be a string")
        if type(self.color_binding) is not WorkflowPayloadColorBinding:
            raise TypeError("color_binding must be WorkflowPayloadColorBinding")


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceAssemblyResult:
    """Exactly one assembled reference or closed assembly failure."""

    reference: WorkflowDomainPayloadReference | None = None
    failure: WorkflowDomainPayloadReferenceAssemblyFailure | None = None

    def __post_init__(self) -> None:
        if (self.reference is None) == (self.failure is None):
            raise ValueError("exactly one assembly result is required")
        if self.reference is not None and (
            type(self.reference) is not WorkflowDomainPayloadReference
        ):
            raise TypeError("reference has the wrong type")
        if self.failure is not None and (
            type(self.failure)
            is not WorkflowDomainPayloadReferenceAssemblyFailure
        ):
            raise TypeError("failure has the wrong type")


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceAssemblerIdentity:
    """Identity of exact payload-reference assembly semantics."""

    value: str = "projectkoios.workflow.payload-reference-assembler:1"


@final
class WorkflowDomainPayloadReferenceAssembler:
    """Compute byte correlations and combine one store-issued identity."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowDomainPayloadReferenceAssemblerIdentity:
        """Return exact payload-reference assembly semantics identity."""
        return WorkflowDomainPayloadReferenceAssemblerIdentity()

    def execute(
        self, request: WorkflowDomainPayloadReferenceAssemblyRequest
    ) -> WorkflowDomainPayloadReferenceAssemblyResult:
        """Return a reference without accepting claimed digest or size values."""
        if type(request) is not WorkflowDomainPayloadReferenceAssemblyRequest:
            raise TypeError(
                "request must be WorkflowDomainPayloadReferenceAssemblyRequest"
            )
        payload_bytes = request.payload_bytes
        binding = request.color_binding
        metadata = request.encoding_metadata
        if not payload_bytes:
            return WorkflowDomainPayloadReferenceAssemblyResult(
                failure=WorkflowDomainPayloadReferenceAssemblyFailure(
                    WorkflowDomainPayloadReferenceAssemblyFailureCode.EMPTY_PAYLOAD,
                    ("payload_bytes",),
                    "payload bytes must not be empty",
                )
            )
        if len(payload_bytes) > binding.maximum_payload_bytes:
            return WorkflowDomainPayloadReferenceAssemblyResult(
                failure=WorkflowDomainPayloadReferenceAssemblyFailure(
                    WorkflowDomainPayloadReferenceAssemblyFailureCode.PAYLOAD_TOO_LARGE,
                    ("payload_bytes",),
                    "payload bytes exceed the compiled binding bound",
                )
            )
        if metadata.schema_identity != binding.payload_schema_identity:
            return WorkflowDomainPayloadReferenceAssemblyResult(
                failure=WorkflowDomainPayloadReferenceAssemblyFailure(
                    WorkflowDomainPayloadReferenceAssemblyFailureCode.SCHEMA_MISMATCH,
                    ("encoding_metadata", "schema_identity"),
                    "owner schema differs from the compiled binding",
                )
            )
        if metadata.media_type != binding.media_type_identity:
            return WorkflowDomainPayloadReferenceAssemblyResult(
                failure=WorkflowDomainPayloadReferenceAssemblyFailure(
                    WorkflowDomainPayloadReferenceAssemblyFailureCode.MEDIA_TYPE_MISMATCH,
                    ("encoding_metadata", "media_type"),
                    "owner media type differs from the compiled binding",
                )
            )
        try:
            reference = WorkflowDomainPayloadReference(
                payload_identity=metadata.payload_identity,
                schema_identity=metadata.schema_identity,
                media_type=metadata.media_type,
                sha256=sha256(payload_bytes).hexdigest(),
                byte_size=len(payload_bytes),
                artifact_identity=request.artifact_identity,
            )
        except TypeError, ValueError:
            return WorkflowDomainPayloadReferenceAssemblyResult(
                failure=WorkflowDomainPayloadReferenceAssemblyFailure(
                    WorkflowDomainPayloadReferenceAssemblyFailureCode.INVALID_ARTIFACT_IDENTITY,
                    ("artifact_identity",),
                    "artifact identity is not a bounded path-free locator",
                )
            )
        return WorkflowDomainPayloadReferenceAssemblyResult(reference=reference)
