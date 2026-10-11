"""Strict canonical control-record transport."""

import json
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits
from typing import cast, final

from ...canonical.json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
    CpnCanonicalJsonParser,
    CpnCanonicalJsonParsingInput,
)
from ...values import (
    CpnControlRecord,
    CpnControlRecordTypeDefinition,
    CpnValue,
    CpnValueKind,
)
from .schema import (
    CpnControlRecordSchemaValidationInput,
    CpnControlRecordSchemaValidator,
)
from .value_canonical import (
    CpnValueCanonicalDecoder,
    CpnValueCanonicalDecodingInput,
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)

_CONTROL_RECORD_PROFILE = "projectkoios.workflow.cpn-control-record-json:0.1.0"
_CONTROL_RECORD_IDENTITY_DOMAIN = (
    "projectkoios.workflow.cpn-control-record:0.1:"
)
_CONTROL_RECORD_CODEC_IDENTITY = (
    "projectkoios.workflow.cpn.control-record-canonical-codec:0.1"
)


@dataclass(frozen=True, slots=True)
class CpnControlRecordCanonicalCodecIdentity:
    """Identity of exact canonical control-record codec semantics."""

    value: str = _CONTROL_RECORD_CODEC_IDENTITY


@dataclass(frozen=True, slots=True)
class CpnCanonicalControlRecordIdentity:
    """Domain-separated identity of exact canonical record bytes."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity value must be a string")
        if not self.value.startswith(_CONTROL_RECORD_IDENTITY_DOMAIN):
            raise ValueError("canonical record identity has the wrong domain")
        digest = self.value.removeprefix(_CONTROL_RECORD_IDENTITY_DOMAIN)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError(
                "canonical record identity must end in lowercase SHA-256"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalControlRecord:
    """Exact canonical record bytes and content-derived identity metadata."""

    canonical_bytes: bytes
    representation_profile_identity: str = field(init=False)
    sha256: str = field(init=False)
    identity: CpnCanonicalControlRecordIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not 1 <= len(self.canonical_bytes) <= 65_536:
            raise ValueError("canonical_bytes must contain 1..65536 bytes")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self, "representation_profile_identity", _CONTROL_RECORD_PROFILE
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            CpnCanonicalControlRecordIdentity(
                _CONTROL_RECORD_IDENTITY_DOMAIN + digest
            ),
        )


@dataclass(frozen=True, slots=True)
class CpnControlRecordCanonicalEncodingInput:
    """One record and exact retained schemas to encode."""

    record: CpnControlRecord
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...]

    def __post_init__(self) -> None:
        if type(self.record) is not CpnControlRecord:
            raise TypeError("record must be CpnControlRecord")
        if type(self.type_definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.type_definitions
        ):
            raise TypeError(
                "type_definitions must be a tuple of "
                "CpnControlRecordTypeDefinition"
            )


@dataclass(frozen=True, slots=True)
class CpnControlRecordCanonicalDecodingInput:
    """Canonical bytes, exact schemas, and optional expected identity."""

    document: CpnCanonicalControlRecord
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...]
    expected_identity: CpnCanonicalControlRecordIdentity | None = None

    def __post_init__(self) -> None:
        if type(self.document) is not CpnCanonicalControlRecord:
            raise TypeError("document must be CpnCanonicalControlRecord")
        if type(self.type_definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.type_definitions
        ):
            raise TypeError(
                "type_definitions must be a tuple of "
                "CpnControlRecordTypeDefinition"
            )
        if (
            self.expected_identity is not None
            and type(self.expected_identity)
            is not CpnCanonicalControlRecordIdentity
        ):
            raise TypeError(
                "expected_identity must be CpnCanonicalControlRecordIdentity or None"
            )


@dataclass(frozen=True, slots=True)
class CpnControlRecordCanonicalDecodingResult:
    """One typed record reconstructed from exact canonical bytes."""

    record: CpnControlRecord

    def __post_init__(self) -> None:
        if type(self.record) is not CpnControlRecord:
            raise TypeError("record must be CpnControlRecord")


@final
class CpnControlRecordCanonicalCodec:
    """Directly encode and strictly decode one bounded control record."""

    __slots__ = ()

    @property
    def identity(self) -> CpnControlRecordCanonicalCodecIdentity:
        """Return the exact codec semantics identity."""
        return CpnControlRecordCanonicalCodecIdentity()

    def encode(
        self, encoding_input: CpnControlRecordCanonicalEncodingInput
    ) -> CpnCanonicalControlRecord:
        """Schema-validate and encode one exact tagged record document."""
        if type(encoding_input) is not CpnControlRecordCanonicalEncodingInput:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_ARGUMENT,
                (),
                "encoding_input must be CpnControlRecordCanonicalEncodingInput",
            )
        validation = CpnControlRecordSchemaValidator().execute(
            CpnControlRecordSchemaValidationInput(
                encoding_input.record, encoding_input.type_definitions
            )
        )
        if not validation.is_valid:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.SCHEMA_VIOLATION,
                validation.issues[0].path,
                validation.issues[0].code.value,
            )
        value = CpnValue(CpnValueKind.CONTROL_RECORD, encoding_input.record)
        state = json.loads(
            CpnValueCanonicalizer()
            .execute(CpnValueCanonicalizationInput(value))
            .canonical_bytes
        )
        try:
            encoded = json.dumps(
                {"profile": _CONTROL_RECORD_PROFILE, "record": state},
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        except (
            OverflowError,
            RecursionError,
            TypeError,
            ValueError,
            UnicodeError,
        ) as exc:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_FIELD,
                (),
                "record cannot be represented canonically",
            ) from exc
        if len(encoded) > 65_536:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.DOCUMENT_TOO_LARGE,
                (),
                "canonical record exceeds 65536 bytes",
            )
        return CpnCanonicalControlRecord(encoded)

    def decode(
        self, decoding_input: CpnControlRecordCanonicalDecodingInput
    ) -> CpnControlRecordCanonicalDecodingResult:
        """Parse, reconstruct, validate, re-encode, and correlate one record."""
        if type(decoding_input) is not CpnControlRecordCanonicalDecodingInput:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_ARGUMENT,
                (),
                "decoding_input must be CpnControlRecordCanonicalDecodingInput",
            )
        document = decoding_input.document
        if (
            decoding_input.expected_identity is not None
            and document.identity != decoding_input.expected_identity
        ):
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                ("identity",),
                "document identity differs from expected identity",
            )
        state = json.loads(
            CpnCanonicalJsonParser()
            .execute(CpnCanonicalJsonParsingInput(document.canonical_bytes))
            .canonical_bytes
        )
        if type(state) is not dict or set(state) != {"profile", "record"}:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_SHAPE,
                (),
                "document must contain exact profile and record fields",
            )
        root = cast(dict[str, object], state)
        if root["profile"] != _CONTROL_RECORD_PROFILE:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.UNSUPPORTED_PROFILE,
                ("profile",),
                "unsupported control-record representation profile",
            )
        record_state = root["record"]
        if (
            type(record_state) is not list
            or len(record_state) != 3
            or record_state[0] != "control_record"
            or type(record_state[1]) is not str
            or type(record_state[2]) is not list
        ):
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_SHAPE,
                ("record",),
                "record state must use the exact tagged array representation",
            )
        try:
            decoded = CpnValueCanonicalDecoder().execute(
                CpnValueCanonicalDecodingInput(
                    CpnValueKind.CONTROL_RECORD.value,
                    json.dumps(
                        record_state,
                        ensure_ascii=False,
                        allow_nan=False,
                        separators=(",", ":"),
                    ).encode("utf-8"),
                    decoding_input.type_definitions,
                )
            )
        except (
            OverflowError,
            RecursionError,
            TypeError,
            UnicodeError,
            ValueError,
        ) as exc:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_FIELD,
                ("record",),
                "record violates its exact tagged representation or schema",
            ) from exc
        assert type(decoded.value.value) is CpnControlRecord
        record = decoded.value.value
        reconstructed = self.encode(
            CpnControlRecordCanonicalEncodingInput(
                record, decoding_input.type_definitions
            )
        )
        if reconstructed.canonical_bytes != document.canonical_bytes:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES,
                (),
                "document has a noncanonical semantic representation",
            )
        return CpnControlRecordCanonicalDecodingResult(record)
