"""Bounded inline owner payload contracts for the Workflow SDK alpha."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ._validation import (
    MAX_INLINE_PAYLOAD_BYTES,
    validate_media_type,
    validate_positive_int,
    validate_sha256,
    validate_token,
)
from .identities import (
    WorkflowPayloadCodecIdentity,
    WorkflowPayloadOwnerIdentity,
    WorkflowPayloadRepresentationIdentity,
    WorkflowPayloadSchemaIdentity,
    WorkflowPayloadTypeIdentity,
)


@dataclass(frozen=True, slots=True)
class WorkflowPayloadContract:
    """Declare one exact bounded owner payload role and representation."""

    role: str
    owner_identity: WorkflowPayloadOwnerIdentity
    payload_type_identity: WorkflowPayloadTypeIdentity
    schema_identity: WorkflowPayloadSchemaIdentity
    codec_identity: WorkflowPayloadCodecIdentity
    representation_identity: WorkflowPayloadRepresentationIdentity
    media_type: str
    maximum_byte_length: int

    def __post_init__(self) -> None:
        validate_token(self.role, "role")
        _require_payload_identity_types(self)
        validate_media_type(self.media_type)
        validate_positive_int(
            self.maximum_byte_length,
            "maximum_byte_length",
            MAX_INLINE_PAYLOAD_BYTES,
        )


@dataclass(frozen=True, slots=True)
class WorkflowInlinePayload:
    """Carry one bounded canonical owner payload as exact inline bytes."""

    role: str
    owner_identity: WorkflowPayloadOwnerIdentity
    payload_type_identity: WorkflowPayloadTypeIdentity
    schema_identity: WorkflowPayloadSchemaIdentity
    codec_identity: WorkflowPayloadCodecIdentity
    representation_identity: WorkflowPayloadRepresentationIdentity
    media_type: str
    payload: bytes
    byte_length: int
    payload_sha256: str

    def __post_init__(self) -> None:
        validate_token(self.role, "role")
        _require_payload_identity_types(self)
        validate_media_type(self.media_type)
        if type(self.payload) is not bytes:
            raise TypeError("payload must be built-in bytes")
        if not self.payload or len(self.payload) > MAX_INLINE_PAYLOAD_BYTES:
            raise ValueError(
                f"payload must contain 1..{MAX_INLINE_PAYLOAD_BYTES} bytes"
            )
        if type(self.byte_length) is not int:
            raise TypeError("byte_length must be a built-in int")
        if self.byte_length != len(self.payload):
            raise ValueError("byte_length differs from payload")
        validate_sha256(self.payload_sha256, "payload_sha256")
        if self.payload_sha256 != hashlib.sha256(self.payload).hexdigest():
            raise ValueError("payload_sha256 differs from payload")


def _require_payload_identity_types(
    value: WorkflowPayloadContract | WorkflowInlinePayload,
) -> None:
    expected = (
        ("owner_identity", WorkflowPayloadOwnerIdentity),
        ("payload_type_identity", WorkflowPayloadTypeIdentity),
        ("schema_identity", WorkflowPayloadSchemaIdentity),
        ("codec_identity", WorkflowPayloadCodecIdentity),
        ("representation_identity", WorkflowPayloadRepresentationIdentity),
    )
    for field_name, field_type in expected:
        if type(getattr(value, field_name)) is not field_type:
            raise TypeError(f"{field_name} must be {field_type.__name__}")


def payload_contract_state(value: WorkflowPayloadContract) -> list[object]:
    """Return private canonical semantic state for one payload contract."""
    return [
        value.role,
        value.owner_identity.value,
        value.payload_type_identity.value,
        value.schema_identity.value,
        value.codec_identity.value,
        value.representation_identity.value,
        value.media_type,
        value.maximum_byte_length,
    ]


def payload_state(value: WorkflowInlinePayload) -> list[object]:
    """Return private canonical semantic state excluding inline byte duplication."""
    return [
        value.role,
        value.owner_identity.value,
        value.payload_type_identity.value,
        value.schema_identity.value,
        value.codec_identity.value,
        value.representation_identity.value,
        value.media_type,
        value.byte_length,
        value.payload_sha256,
    ]


__all__ = ["WorkflowInlinePayload", "WorkflowPayloadContract"]
