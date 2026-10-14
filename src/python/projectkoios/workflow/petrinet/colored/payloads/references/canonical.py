"""Canonical transport for six-field retained owner-payload references."""

import json
from dataclasses import dataclass, field
from hashlib import sha256
from typing import final

from ...canonical.json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
)
from .definition import (
    WorkflowDomainPayloadReference,
    WorkflowDomainPayloadReferenceIdentity,
)

_REFERENCE_PROFILE = "projectkoios.workflow.payload-reference-json:1"
_MAXIMUM_REFERENCE_BYTES = 4096
_REFERENCE_IDENTITY_PREFIX = "projectkoios.workflow.payload-reference:1:"


@dataclass(frozen=True, slots=True)
class WorkflowCanonicalDomainPayloadReference:
    """Exact canonical bytes for one retained owner-payload reference."""

    canonical_bytes: bytes
    representation_profile_identity: str = field(init=False)
    sha256: str = field(init=False)
    identity: WorkflowDomainPayloadReferenceIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not self.canonical_bytes:
            raise ValueError("canonical_bytes must not be empty")
        if len(self.canonical_bytes) > _MAXIMUM_REFERENCE_BYTES:
            raise ValueError("canonical payload reference exceeds byte bound")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self,
            "representation_profile_identity",
            _REFERENCE_PROFILE,
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            WorkflowDomainPayloadReferenceIdentity(
                _REFERENCE_IDENTITY_PREFIX + digest
            ),
        )


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceEncodingInput:
    """Typed payload reference requested for exact canonical encoding."""

    reference: WorkflowDomainPayloadReference

    def __post_init__(self) -> None:
        if type(self.reference) is not WorkflowDomainPayloadReference:
            raise TypeError("reference must be WorkflowDomainPayloadReference")


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceDecodingInput:
    """Canonical reference bytes and the exact retained claimed identity."""

    canonical_reference: WorkflowCanonicalDomainPayloadReference
    claimed_identity: WorkflowDomainPayloadReferenceIdentity

    def __post_init__(self) -> None:
        if (
            type(self.canonical_reference)
            is not WorkflowCanonicalDomainPayloadReference
        ):
            raise TypeError(
                "canonical_reference must be WorkflowCanonicalDomainPayloadReference"
            )
        if (
            type(self.claimed_identity)
            is not WorkflowDomainPayloadReferenceIdentity
        ):
            raise TypeError(
                "claimed_identity must be WorkflowDomainPayloadReferenceIdentity"
            )


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceDecodingResult:
    """One strictly reconstructed immutable payload reference."""

    reference: WorkflowDomainPayloadReference

    def __post_init__(self) -> None:
        if type(self.reference) is not WorkflowDomainPayloadReference:
            raise TypeError("reference must be WorkflowDomainPayloadReference")


@dataclass(frozen=True, slots=True)
class WorkflowDomainPayloadReferenceCodecIdentity:
    """Identity of the exact canonical payload-reference transport."""

    value: str = "projectkoios.workflow.payload-reference-codec:1"


@final
class WorkflowDomainPayloadReferenceCodec:
    """Encode and strictly reconstruct path-free payload references."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowDomainPayloadReferenceCodecIdentity:
        """Return exact canonical payload-reference transport identity."""
        return WorkflowDomainPayloadReferenceCodecIdentity()

    def encode(
        self, encoding_input: WorkflowDomainPayloadReferenceEncodingInput
    ) -> WorkflowCanonicalDomainPayloadReference:
        """Encode exactly the six normative reference fields."""
        if (
            type(encoding_input)
            is not WorkflowDomainPayloadReferenceEncodingInput
        ):
            raise TypeError(
                "encoding_input must be WorkflowDomainPayloadReferenceEncodingInput"
            )
        reference = encoding_input.reference
        state = {
            "artifact_identity": reference.artifact_identity,
            "byte_size": reference.byte_size,
            "media_type": reference.media_type,
            "payload_identity": reference.payload_identity,
            "schema_identity": reference.schema_identity,
            "sha256": reference.sha256,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(encoded) > _MAXIMUM_REFERENCE_BYTES:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.DOCUMENT_TOO_LARGE,
                (),
                "canonical payload reference exceeds byte bound",
            )
        document = WorkflowCanonicalDomainPayloadReference(encoded)
        if document.identity != reference.identity:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                ("identity",),
                "reference identity differs from canonical bytes",
            )
        return document

    def decode(
        self, decoding_input: WorkflowDomainPayloadReferenceDecodingInput
    ) -> WorkflowDomainPayloadReferenceDecodingResult:
        """Reject malformed, substituted, or noncanonical reference bytes."""
        if (
            type(decoding_input)
            is not WorkflowDomainPayloadReferenceDecodingInput
        ):
            raise TypeError(
                "decoding_input must be WorkflowDomainPayloadReferenceDecodingInput"
            )
        document = decoding_input.canonical_reference
        if decoding_input.claimed_identity != document.identity:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                ("identity",),
                "claimed identity differs from canonical reference bytes",
            )
        try:
            text = document.canonical_bytes.decode("utf-8")
            pairs = json.loads(text, object_pairs_hook=tuple)
            if type(pairs) is not tuple:
                raise TypeError("root must be an object")
            state: dict[str, str | int] = {}
            for pair in pairs:
                if (
                    type(pair) is not tuple
                    or len(pair) != 2
                    or type(pair[0]) is not str
                ):
                    raise TypeError("object pair is invalid")
                if pair[0] in state:
                    raise CpnCanonicalCodecError(
                        CpnCanonicalCodecErrorCode.DUPLICATE_KEY,
                        (pair[0],),
                        "duplicate object key",
                    )
                if type(pair[1]) not in (str, int):
                    raise TypeError("reference field has an invalid type")
                state[pair[0]] = pair[1]
            expected = {
                "artifact_identity",
                "byte_size",
                "media_type",
                "payload_identity",
                "schema_identity",
                "sha256",
            }
            if set(state) != expected:
                raise TypeError("reference field set is invalid")
            string_names = (
                "artifact_identity",
                "media_type",
                "payload_identity",
                "schema_identity",
                "sha256",
            )
            if any(type(state[name]) is not str for name in string_names):
                raise TypeError("reference string field has an invalid type")
            byte_size = state["byte_size"]
            if type(byte_size) is not int:
                raise TypeError("byte_size must be an integer")
            reference = WorkflowDomainPayloadReference(
                payload_identity=state["payload_identity"],  # type: ignore[arg-type]
                schema_identity=state["schema_identity"],  # type: ignore[arg-type]
                media_type=state["media_type"],  # type: ignore[arg-type]
                sha256=state["sha256"],  # type: ignore[arg-type]
                byte_size=byte_size,
                artifact_identity=state["artifact_identity"],  # type: ignore[arg-type]
            )
        except CpnCanonicalCodecError:
            raise
        except (
            json.JSONDecodeError,
            KeyError,
            OverflowError,
            RecursionError,
            TypeError,
            UnicodeError,
            ValueError,
        ) as exc:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_SHAPE,
                (),
                f"payload-reference decoding failed: {type(exc).__name__}",
            ) from exc
        reencoded = self.encode(
            WorkflowDomainPayloadReferenceEncodingInput(reference)
        )
        if reencoded.canonical_bytes != document.canonical_bytes:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES,
                (),
                "payload-reference bytes differ from exact re-encoding",
            )
        if reference.identity != decoding_input.claimed_identity:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                ("identity",),
                "reconstructed reference identity differs from retained identity",
            )
        return WorkflowDomainPayloadReferenceDecodingResult(reference)
