"""Canonical transport for explicit CPN selection directives."""

import json
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits
from typing import final

from ..enablement.outcomes import (
    CpnEnablementResultIdentity,
)
from ..selection import (
    CpnSelectionDirective,
    CpnSelectionDirectiveIdentity,
)
from .bindings import (
    CpnCanonicalBinding,
    CpnCanonicalBindingCodec,
    CpnCanonicalBindingDecodingInput,
    CpnCanonicalBindingEncodingInput,
)
from ..values import CpnControlRecordTypeDefinition
from .json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
    CpnCanonicalJsonParser,
    CpnCanonicalJsonParsingInput,
)

_DIRECTIVE_PROFILE = "projectkoios.workflow.cpn-selection-directive-json:0.1.0"
_MAXIMUM_DIRECTIVE_BYTES = 2_200_000


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionDirectiveIdentity:
    """Content-derived identity of exact canonical directive bytes."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity must be a string")
        prefix = "projectkoios.workflow.cpn-selection-directive:0.1:"
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
class CpnCanonicalSelectionDirective:
    """Exact directive bytes and constructor-derived correlations."""

    canonical_bytes: bytes
    representation_profile_identity: str = field(init=False)
    sha256: str = field(init=False)
    identity: CpnCanonicalSelectionDirectiveIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not self.canonical_bytes:
            raise ValueError("canonical_bytes must not be empty")
        if len(self.canonical_bytes) > _MAXIMUM_DIRECTIVE_BYTES:
            raise ValueError("canonical directive exceeds byte bound")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self, "representation_profile_identity", _DIRECTIVE_PROFILE
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            CpnCanonicalSelectionDirectiveIdentity(
                "projectkoios.workflow.cpn-selection-directive:0.1:" + digest
            ),
        )


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionDirectiveEncodingInput:
    """One exact selection directive requested for canonical encoding."""

    directive: CpnSelectionDirective

    def __post_init__(self) -> None:
        if type(self.directive) is not CpnSelectionDirective:
            raise TypeError("directive must be CpnSelectionDirective")


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionDirectiveDecodingInput:
    """One canonical directive and exact retained record schemas."""

    canonical_directive: CpnCanonicalSelectionDirective
    control_record_types: tuple[CpnControlRecordTypeDefinition, ...] = ()

    def __post_init__(self) -> None:
        if type(self.canonical_directive) is not CpnCanonicalSelectionDirective:
            raise TypeError(
                "canonical_directive must be CpnCanonicalSelectionDirective"
            )
        if type(self.control_record_types) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.control_record_types
        ):
            raise TypeError(
                "control_record_types must contain exact type definitions"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionDirectiveDecodingResult:
    """One admitted directive reconstructed from canonical bytes."""

    directive: CpnSelectionDirective

    def __post_init__(self) -> None:
        if type(self.directive) is not CpnSelectionDirective:
            raise TypeError("directive must be CpnSelectionDirective")


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionDirectiveCodecIdentity:
    """Identity of exact canonical directive transport semantics."""

    value: str = (
        "projectkoios.workflow.cpn.canonical-selection-directive-codec:0.1"
    )


@final
class CpnCanonicalSelectionDirectiveCodec:
    """Encode and strictly reconstruct explicit selection directives."""

    __slots__ = ()

    @property
    def identity(self) -> CpnCanonicalSelectionDirectiveCodecIdentity:
        """Return exact directive transport semantics identity."""
        return CpnCanonicalSelectionDirectiveCodecIdentity()

    def encode(
        self,
        encoding_input: CpnCanonicalSelectionDirectiveEncodingInput,
    ) -> CpnCanonicalSelectionDirective:
        """Encode one directive with its complete canonical binding bytes."""
        if type(encoding_input) is not (
            CpnCanonicalSelectionDirectiveEncodingInput
        ):
            raise TypeError(
                "encoding_input must be "
                "CpnCanonicalSelectionDirectiveEncodingInput"
            )
        directive = encoding_input.directive
        binding = CpnCanonicalBindingCodec().encode(
            CpnCanonicalBindingEncodingInput(directive.binding)
        )
        state = {
            "binding_canonical_bytes_hex": binding.canonical_bytes.hex(),
            "directive_identity": directive.identity.value,
            "enablement_result_identity": (
                directive.enablement_result_identity.value
            ),
            "profile": _DIRECTIVE_PROFILE,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(encoded) > _MAXIMUM_DIRECTIVE_BYTES:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.DOCUMENT_TOO_LARGE,
                (),
                "canonical directive exceeds byte bound",
            )
        return CpnCanonicalSelectionDirective(encoded)

    def decode(
        self,
        decoding_input: CpnCanonicalSelectionDirectiveDecodingInput,
    ) -> CpnCanonicalSelectionDirectiveDecodingResult:
        """Parse, reconstruct, correlate, and exactly re-encode a directive."""
        if type(decoding_input) is not (
            CpnCanonicalSelectionDirectiveDecodingInput
        ):
            raise TypeError(
                "decoding_input must be "
                "CpnCanonicalSelectionDirectiveDecodingInput"
            )
        document = decoding_input.canonical_directive
        try:
            state = json.loads(
                CpnCanonicalJsonParser()
                .execute(CpnCanonicalJsonParsingInput(document.canonical_bytes))
                .canonical_bytes
            )
            if type(state) is not dict or set(state) != {
                "binding_canonical_bytes_hex",
                "directive_identity",
                "enablement_result_identity",
                "profile",
            }:
                raise TypeError("root shape")
            if state["profile"] != _DIRECTIVE_PROFILE:
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.UNSUPPORTED_PROFILE,
                    ("profile",),
                    "unsupported canonical directive profile",
                )
            binding_hex = state["binding_canonical_bytes_hex"]
            directive_identity = state["directive_identity"]
            enablement_identity = state["enablement_result_identity"]
            if any(
                type(item) is not str
                for item in (
                    binding_hex,
                    directive_identity,
                    enablement_identity,
                )
            ):
                raise TypeError("directive fields")
            binding = (
                CpnCanonicalBindingCodec()
                .decode(
                    CpnCanonicalBindingDecodingInput(
                        CpnCanonicalBinding(bytes.fromhex(binding_hex)),
                        decoding_input.control_record_types,
                    )
                )
                .binding
            )
            directive = CpnSelectionDirective(
                CpnEnablementResultIdentity(enablement_identity), binding
            )
            if directive.identity != CpnSelectionDirectiveIdentity(
                directive_identity
            ):
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                    ("directive_identity",),
                    "directive identity differs from reconstructed content",
                )
        except CpnCanonicalCodecError:
            raise
        except (
            AttributeError,
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
                f"directive decoding failed: {type(exc).__name__}",
            ) from exc
        reencoded = self.encode(
            CpnCanonicalSelectionDirectiveEncodingInput(directive)
        )
        if reencoded.canonical_bytes != document.canonical_bytes:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES,
                (),
                "directive bytes differ from exact re-encoding",
            )
        return CpnCanonicalSelectionDirectiveDecodingResult(directive)
