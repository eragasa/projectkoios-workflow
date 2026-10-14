"""Immutable path-free references to retained owner payload bytes."""

import json
from dataclasses import dataclass
from hashlib import sha256
from string import hexdigits

_MAXIMUM_IDENTITY_BYTES = 512
_MAXIMUM_SIGNED_64 = 9_223_372_036_854_775_807
_REFERENCE_IDENTITY_PREFIX = "projectkoios.workflow.payload-reference:1:"


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceIdentity:
    """Content identity of one complete canonical payload-reference record."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("payload-reference identity must be a string")
        if not self.value.startswith(_REFERENCE_IDENTITY_PREFIX):
            raise ValueError("payload-reference identity has the wrong domain")
        digest = self.value.removeprefix(_REFERENCE_IDENTITY_PREFIX)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(character in hexdigits for character in digest)
        ):
            raise ValueError(
                "payload-reference identity must end in lowercase SHA-256"
            )


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadEncodingMetadata:
    """Owner-derived semantic metadata accompanying canonical payload bytes."""

    payload_identity: str
    schema_identity: str
    media_type: str

    def __post_init__(self) -> None:
        for name in ("payload_identity", "schema_identity"):
            value = getattr(self, name)
            if (
                type(value) is not str
                or not value
                or not value.isascii()
                or len(value.encode("ascii")) > _MAXIMUM_IDENTITY_BYTES
                or any(
                    ord(character) < 32 or ord(character) == 127
                    for character in value
                )
            ):
                raise ValueError(f"{name} must be bounded nonempty ASCII")
        if (
            type(self.media_type) is not str
            or not self.media_type.isascii()
            or len(self.media_type.encode("ascii")) > _MAXIMUM_IDENTITY_BYTES
        ):
            raise ValueError("media_type must be bounded ASCII")
        parts = self.media_type.split("/", 1)
        subtype = "" if len(parts) != 2 else parts[1]
        structured_suffix_stem = (
            subtype.removesuffix("+json") if subtype.endswith("+json") else ""
        )
        if not (
            len(parts) == 2
            and parts[0] == "application"
            and (
                subtype == "json"
                or (
                    structured_suffix_stem
                    and all(
                        character.isalnum() or character in "!#$&^_.-"
                        for character in structured_suffix_stem
                    )
                )
            )
        ):
            raise ValueError(
                "media_type must be application/json or application/*+json"
            )


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReference:
    """Six-field immutable locator and exact-byte correlation record."""

    payload_identity: str
    schema_identity: str
    media_type: str
    sha256: str
    byte_size: int
    artifact_identity: str

    def __post_init__(self) -> None:
        WorkflowDomainPayloadEncodingMetadata(
            self.payload_identity,
            self.schema_identity,
            self.media_type,
        )
        if not (
            type(self.sha256) is str
            and len(self.sha256) == 64
            and self.sha256 == self.sha256.lower()
            and all(character in hexdigits for character in self.sha256)
        ):
            raise ValueError("sha256 must be lowercase SHA-256")
        if (
            type(self.byte_size) is not int
            or not 1 <= self.byte_size <= _MAXIMUM_SIGNED_64
        ):
            raise ValueError(
                "byte_size must be a positive signed 64-bit integer"
            )
        artifact = self.artifact_identity
        if (
            type(artifact) is not str
            or not artifact
            or not artifact.isascii()
            or len(artifact.encode("ascii")) > _MAXIMUM_IDENTITY_BYTES
            or any(
                ord(character) < 32 or ord(character) == 127
                for character in artifact
            )
        ):
            raise ValueError("artifact_identity must be bounded nonempty ASCII")
        if artifact.startswith(("/", "~/", "\\", "file:")) or (
            len(artifact) >= 3
            and artifact[0].isalpha()
            and artifact[1] == ":"
            and artifact[2] in ("/", "\\")
        ):
            raise ValueError("artifact_identity must exclude machine paths")

    @property
    def identity(self) -> WorkflowDomainPayloadReferenceIdentity:
        """Derive the complete reference-record identity without storing it."""
        state = {
            "artifact_identity": self.artifact_identity,
            "byte_size": self.byte_size,
            "media_type": self.media_type,
            "payload_identity": self.payload_identity,
            "schema_identity": self.schema_identity,
            "sha256": self.sha256,
        }
        canonical_bytes = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return WorkflowDomainPayloadReferenceIdentity(
            _REFERENCE_IDENTITY_PREFIX + sha256(canonical_bytes).hexdigest()
        )
