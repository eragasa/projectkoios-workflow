"""Exact canonical marking representation and content identity."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits
from typing import final

from .json import CpnCanonicalJsonParser, CpnCanonicalJsonParsingInput
from ..control.records.value_canonical import (
    CpnValueCanonicalDecoder,
    CpnValueCanonicalDecodingInput,
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from ..definitions import CpnDefinition, CpnDefinitionIdentity, CpnPlaceIdentity
from ..markings import CpnMarking, CpnMarkingIdentity, CpnPlaceMarking
from ..values import CpnColorIdentity, CpnToken, CpnTokenIdentity

_MARKING_PROFILE = "projectkoios.workflow.cpn-marking-json:0.1.0"
_MARKING_IDENTITY_DOMAIN = "projectkoios.workflow.cpn-marking:0.1:"
_MAXIMUM_MARKING_BYTES = 1_048_576


@dataclass(frozen=True, slots=True)
class CpnCanonicalMarkingCodecIdentity:
    """Identity of exact canonical marking encoding semantics."""

    value: str = "projectkoios.workflow.cpn.canonical-marking-codec:0.1"


@dataclass(frozen=True, slots=True)
class CpnCanonicalMarkingIdentity:
    """Domain-separated identity of exact canonical marking bytes."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity value must be a string")
        if not self.value.startswith(_MARKING_IDENTITY_DOMAIN):
            raise ValueError("canonical marking identity has the wrong domain")
        digest = self.value.removeprefix(_MARKING_IDENTITY_DOMAIN)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError(
                "canonical marking identity must end in lowercase SHA-256"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalMarking:
    """Exact canonical marking bytes and derived correlation metadata."""

    canonical_bytes: bytes
    representation_profile_identity: str = field(init=False)
    sha256: str = field(init=False)
    identity: CpnCanonicalMarkingIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not 1 <= len(self.canonical_bytes) <= _MAXIMUM_MARKING_BYTES:
            raise ValueError("canonical marking exceeds its byte bound")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self, "representation_profile_identity", _MARKING_PROFILE
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            CpnCanonicalMarkingIdentity(_MARKING_IDENTITY_DOMAIN + digest),
        )


@dataclass(frozen=True, slots=True)
class CpnCanonicalMarkingEncodingInput:
    """One complete immutable marking to encode."""

    marking: CpnMarking

    def __post_init__(self) -> None:
        if type(self.marking) is not CpnMarking:
            raise TypeError("marking must be CpnMarking")


@dataclass(frozen=True, slots=True)
class CpnCanonicalMarkingDecodingInput:
    """Canonical marking bytes and exact retained flat definition."""

    document: CpnCanonicalMarking
    definition: CpnDefinition

    def __post_init__(self) -> None:
        if type(self.document) is not CpnCanonicalMarking:
            raise TypeError("document must be CpnCanonicalMarking")
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")


@dataclass(frozen=True, slots=True)
class CpnCanonicalMarkingDecodingResult:
    """One reconstructed marking and its exact canonical document."""

    marking: CpnMarking
    document: CpnCanonicalMarking

    def __post_init__(self) -> None:
        if type(self.marking) is not CpnMarking:
            raise TypeError("marking must be CpnMarking")
        if type(self.document) is not CpnCanonicalMarking:
            raise TypeError("document must be CpnCanonicalMarking")


@final
class CpnCanonicalMarkingCodec:
    """Encode complete markings without payload resolution or callbacks."""

    __slots__ = ()

    @property
    def identity(self) -> CpnCanonicalMarkingCodecIdentity:
        """Return exact marking codec semantics identity."""
        return CpnCanonicalMarkingCodecIdentity()

    def encode(
        self, encoding_input: CpnCanonicalMarkingEncodingInput
    ) -> CpnCanonicalMarking:
        """Return deterministic bounded UTF-8 JSON for one marking."""
        if type(encoding_input) is not CpnCanonicalMarkingEncodingInput:
            raise TypeError(
                "encoding_input must be CpnCanonicalMarkingEncodingInput"
            )
        marking = encoding_input.marking
        state = {
            "definition_identity": marking.definition_identity.value,
            "marking_identity": marking.identity.value,
            "places": [
                {
                    "place_identity": place.place_identity.value,
                    "tokens": [
                        {
                            "color_identity": token.color_identity.value,
                            "token_identity": (
                                None
                                if token.token_identity is None
                                else token.token_identity.value
                            ),
                            "value_kind": token.value.kind.value,
                            "value": json.loads(
                                CpnValueCanonicalizer()
                                .execute(
                                    CpnValueCanonicalizationInput(token.value)
                                )
                                .canonical_bytes
                            ),
                        }
                        for token in place.tokens
                    ],
                }
                for place in marking.places
            ],
            "representation_profile_identity": _MARKING_PROFILE,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(encoded) > _MAXIMUM_MARKING_BYTES:
            raise ValueError("canonical marking exceeds its byte bound")
        return CpnCanonicalMarking(encoded)

    def decode(
        self, decoding_input: CpnCanonicalMarkingDecodingInput
    ) -> CpnCanonicalMarkingDecodingResult:
        """Strictly reconstruct transport state without structural validation."""
        if type(decoding_input) is not CpnCanonicalMarkingDecodingInput:
            raise TypeError(
                "decoding_input must be CpnCanonicalMarkingDecodingInput"
            )
        state = json.loads(
            CpnCanonicalJsonParser()
            .execute(
                CpnCanonicalJsonParsingInput(
                    decoding_input.document.canonical_bytes
                )
            )
            .canonical_bytes
        )
        if type(state) is not dict or set(state) != {
            "definition_identity",
            "marking_identity",
            "places",
            "representation_profile_identity",
        }:
            raise ValueError("canonical marking has an invalid root shape")
        if state["representation_profile_identity"] != _MARKING_PROFILE:
            raise ValueError("canonical marking profile is unsupported")
        places_state = state["places"]
        if type(places_state) is not list:
            raise ValueError("canonical marking places must be an array")
        places: list[CpnPlaceMarking] = []
        for place_index, place_state in enumerate(places_state):
            if type(place_state) is not dict or set(place_state) != {
                "place_identity",
                "tokens",
            }:
                raise ValueError(
                    f"canonical marking place {place_index} has invalid shape"
                )
            tokens_state = place_state["tokens"]
            if type(tokens_state) is not list:
                raise ValueError("canonical marking tokens must be an array")
            tokens: list[CpnToken] = []
            for token_index, token_state in enumerate(tokens_state):
                if type(token_state) is not dict or set(token_state) != {
                    "color_identity",
                    "token_identity",
                    "value",
                    "value_kind",
                }:
                    raise ValueError(
                        "canonical marking token "
                        f"{place_index}:{token_index} has invalid shape"
                    )
                color_identity = token_state["color_identity"]
                token_identity = token_state["token_identity"]
                value_kind = token_state["value_kind"]
                if (
                    type(color_identity) is not str
                    or type(value_kind) is not str
                ):
                    raise ValueError(
                        "canonical token identities must be strings"
                    )
                if (
                    token_identity is not None
                    and type(token_identity) is not str
                ):
                    raise ValueError(
                        "canonical token identity must be string or null"
                    )
                value = (
                    CpnValueCanonicalDecoder()
                    .execute(
                        CpnValueCanonicalDecodingInput(
                            value_kind,
                            json.dumps(
                                token_state["value"],
                                ensure_ascii=False,
                                allow_nan=False,
                                separators=(",", ":"),
                            ).encode("utf-8"),
                            decoding_input.definition.control_record_types,
                        )
                    )
                    .value
                )
                tokens.append(
                    CpnToken(
                        CpnColorIdentity(color_identity),
                        value,
                        None
                        if token_identity is None
                        else CpnTokenIdentity(token_identity),
                    )
                )
            place_identity = place_state["place_identity"]
            if type(place_identity) is not str:
                raise ValueError("canonical place identity must be a string")
            places.append(
                CpnPlaceMarking(CpnPlaceIdentity(place_identity), tuple(tokens))
            )
        marking_identity = state["marking_identity"]
        definition_identity = state["definition_identity"]
        if (
            type(marking_identity) is not str
            or type(definition_identity) is not str
        ):
            raise ValueError("canonical marking identities must be strings")
        marking = CpnMarking(
            CpnMarkingIdentity(marking_identity),
            CpnDefinitionIdentity(definition_identity),
            tuple(places),
        )
        replay = self.encode(CpnCanonicalMarkingEncodingInput(marking))
        if replay != decoding_input.document:
            raise ValueError("decoded marking does not replay byte-for-byte")
        return CpnCanonicalMarkingDecodingResult(marking, replay)
