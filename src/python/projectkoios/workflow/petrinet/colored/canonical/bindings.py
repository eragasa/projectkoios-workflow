"""Canonical transport for ordered CPN transition bindings."""

import json
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits
from typing import final

from ..bindings import CpnBinding, CpnBindingAssignment
from ..control.records.value_canonical import (
    CpnValueCanonicalDecoder,
    CpnValueCanonicalDecodingInput,
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from ..definitions import CpnTransitionIdentity
from ..expressions.grammar import CpnBindingVariableIdentity
from ..values import CpnControlRecordTypeDefinition
from .json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
    CpnCanonicalJsonParser,
    CpnCanonicalJsonParsingInput,
)

_BINDING_PROFILE = "projectkoios.workflow.cpn-binding-json:0.1.0"
_MAXIMUM_BINDING_BYTES = 1_048_576


@dataclass(frozen=True, slots=True)
class CpnCanonicalBindingIdentity:
    """Content-derived identity of exact canonical binding bytes."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity must be a string")
        prefix = "projectkoios.workflow.cpn-binding:0.1:"
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
class CpnCanonicalBinding:
    """Exact binding bytes and constructor-derived correlations."""

    canonical_bytes: bytes
    representation_profile_identity: str = field(init=False)
    sha256: str = field(init=False)
    identity: CpnCanonicalBindingIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not self.canonical_bytes:
            raise ValueError("canonical_bytes must not be empty")
        if len(self.canonical_bytes) > _MAXIMUM_BINDING_BYTES:
            raise ValueError("canonical binding exceeds byte bound")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self, "representation_profile_identity", _BINDING_PROFILE
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            CpnCanonicalBindingIdentity(
                "projectkoios.workflow.cpn-binding:0.1:" + digest
            ),
        )


@dataclass(frozen=True, slots=True)
class CpnCanonicalBindingEncodingInput:
    """One exact binding requested for canonical encoding."""

    binding: CpnBinding

    def __post_init__(self) -> None:
        if type(self.binding) is not CpnBinding:
            raise TypeError("binding must be CpnBinding")


@dataclass(frozen=True, slots=True)
class CpnCanonicalBindingDecodingInput:
    """One canonical binding and exact retained control-record schemas."""

    canonical_binding: CpnCanonicalBinding
    control_record_types: tuple[CpnControlRecordTypeDefinition, ...] = ()

    def __post_init__(self) -> None:
        if type(self.canonical_binding) is not CpnCanonicalBinding:
            raise TypeError("canonical_binding must be CpnCanonicalBinding")
        if type(self.control_record_types) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.control_record_types
        ):
            raise TypeError(
                "control_record_types must contain exact type definitions"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalBindingDecodingResult:
    """One admitted binding reconstructed from canonical bytes."""

    binding: CpnBinding

    def __post_init__(self) -> None:
        if type(self.binding) is not CpnBinding:
            raise TypeError("binding must be CpnBinding")


@dataclass(frozen=True, slots=True)
class CpnCanonicalBindingCodecIdentity:
    """Identity of exact canonical binding transport semantics."""

    value: str = "projectkoios.workflow.cpn.canonical-binding-codec:0.1"


@final
class CpnCanonicalBindingCodec:
    """Encode and strictly reconstruct ordered transition bindings."""

    __slots__ = ()

    @property
    def identity(self) -> CpnCanonicalBindingCodecIdentity:
        """Return exact canonical binding transport semantics identity."""
        return CpnCanonicalBindingCodecIdentity()

    def encode(
        self, encoding_input: CpnCanonicalBindingEncodingInput
    ) -> CpnCanonicalBinding:
        """Encode one exact ordered binding without owner callbacks."""
        if type(encoding_input) is not CpnCanonicalBindingEncodingInput:
            raise TypeError(
                "encoding_input must be CpnCanonicalBindingEncodingInput"
            )
        binding = encoding_input.binding
        state = {
            "assignments": [
                [
                    item.variable_identity.value,
                    item.value.kind.value,
                    json.loads(
                        CpnValueCanonicalizer()
                        .execute(CpnValueCanonicalizationInput(item.value))
                        .canonical_bytes
                    ),
                ]
                for item in binding.assignments
            ],
            "profile": _BINDING_PROFILE,
            "transition_identity": binding.transition_identity.value,
        }
        try:
            encoded = json.dumps(
                state,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        except (OverflowError, TypeError, UnicodeError, ValueError) as exc:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_FIELD,
                (),
                f"binding encoding failed: {type(exc).__name__}",
            ) from exc
        if len(encoded) > _MAXIMUM_BINDING_BYTES:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.DOCUMENT_TOO_LARGE,
                (),
                "canonical binding exceeds byte bound",
            )
        return CpnCanonicalBinding(encoded)

    def decode(
        self, decoding_input: CpnCanonicalBindingDecodingInput
    ) -> CpnCanonicalBindingDecodingResult:
        """Parse, reconstruct, and byte-for-byte re-encode one binding."""
        if type(decoding_input) is not CpnCanonicalBindingDecodingInput:
            raise TypeError(
                "decoding_input must be CpnCanonicalBindingDecodingInput"
            )
        document = decoding_input.canonical_binding
        try:
            state = json.loads(
                CpnCanonicalJsonParser()
                .execute(CpnCanonicalJsonParsingInput(document.canonical_bytes))
                .canonical_bytes
            )
            if type(state) is not dict or set(state) != {
                "assignments",
                "profile",
                "transition_identity",
            }:
                raise TypeError("root shape")
            if state["profile"] != _BINDING_PROFILE:
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.UNSUPPORTED_PROFILE,
                    ("profile",),
                    "unsupported canonical binding profile",
                )
            transition = state["transition_identity"]
            assignments_state = state["assignments"]
            if (
                type(transition) is not str
                or type(assignments_state) is not list
            ):
                raise TypeError("binding fields")
            assignments: list[CpnBindingAssignment] = []
            for index, item in enumerate(assignments_state):
                if (
                    type(item) is not list
                    or len(item) != 3
                    or type(item[0]) is not str
                    or type(item[1]) is not str
                ):
                    raise TypeError(f"assignment {index} shape")
                value = (
                    CpnValueCanonicalDecoder()
                    .execute(
                        CpnValueCanonicalDecodingInput(
                            item[1],
                            json.dumps(
                                item[2],
                                ensure_ascii=False,
                                allow_nan=False,
                                separators=(",", ":"),
                            ).encode("utf-8"),
                            decoding_input.control_record_types,
                        )
                    )
                    .value
                )
                assignments.append(
                    CpnBindingAssignment(
                        CpnBindingVariableIdentity(item[0]), value
                    )
                )
            binding = CpnBinding(
                CpnTransitionIdentity(transition), tuple(assignments)
            )
        except CpnCanonicalCodecError:
            raise
        except (
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
                f"binding decoding failed: {type(exc).__name__}",
            ) from exc
        reencoded = self.encode(CpnCanonicalBindingEncodingInput(binding))
        if reencoded.canonical_bytes != document.canonical_bytes:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES,
                (),
                "binding bytes differ from exact re-encoding",
            )
        return CpnCanonicalBindingDecodingResult(binding)
