"""Canonical representation codec for experimental shadow-CPN markings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetColorIdentity,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetMarking,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetPlaceMarking,
    ColoredPetriNetToken,
    ColoredPetriNetTokenIdentity,
)

from ._cpn_representation import (
    MAX_CPN_REPRESENTATION_ITEMS as _MAX_ITEMS,
)
from ._cpn_representation import (
    bounded_text as _bounded,
)
from ._cpn_representation import (
    closed_object as _object,
)
from ._cpn_representation import (
    exact_text as _text,
)
from ._cpn_representation import (
    value_from_state as _value_from_state,
)
from ._cpn_representation import (
    value_state as _value_state,
)

_MARKING_PROFILE = "projectkoios.workflow.experimental-cpn-marking-json:0"
_MAX_MARKING_BYTES = 16 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity:
    """Identity of the bounded canonical semantic-marking representation."""

    value: str

    def __post_init__(self) -> None:
        _bounded(self.value, "marking representation profile identity")


@final
class ExperimentalWorkflowCpnMarkingEncoder:
    """Encode exact shadow-CPN semantic marking state as canonical JSON."""

    __slots__ = ()

    @property
    def profile_identity(
        self,
    ) -> ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity:
        return ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity(
            _MARKING_PROFILE
        )

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowCpnMarkingEncoder is not subclassable"
        )

    def encode(self, marking: ColoredPetriNetMarking) -> bytes:
        """Return the exact bounded representation selected by this profile."""
        if type(marking) is not ColoredPetriNetMarking:
            raise TypeError("marking must be ColoredPetriNetMarking")
        if len(marking.places) > _MAX_ITEMS:
            raise ValueError("marking places exceed their count bound")
        state_places: list[dict[str, object]] = []
        total_tokens = 0
        for place in marking.places:
            if len(place.tokens) > _MAX_ITEMS:
                raise ValueError("place tokens exceed their count bound")
            total_tokens += len(place.tokens)
            if total_tokens > _MAX_ITEMS:
                raise ValueError("marking tokens exceed their count bound")
            state_places.append(
                {
                    "place_identity": _bounded(
                        place.place_identity.value, "marking place identity"
                    ),
                    "tokens": [
                        {
                            "color_identity": _bounded(
                                token.color_identity.value,
                                "token color identity",
                            ),
                            "token_identity": (
                                None
                                if token.token_identity is None
                                else _bounded(
                                    token.token_identity.value,
                                    "token identity",
                                )
                            ),
                            "value": _value_state(token.value),
                        }
                        for token in place.tokens
                    ],
                }
            )
        payload = json.dumps(
            {
                "marking": {
                    "definition_identity": _bounded(
                        marking.definition_identity.value,
                        "marking definition identity",
                    ),
                    "identity": _bounded(
                        marking.identity.value, "marking identity"
                    ),
                    "places": state_places,
                },
                "schema": _MARKING_PROFILE,
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(payload) > _MAX_MARKING_BYTES:
            raise ValueError("encoded marking exceeds its byte bound")
        return payload


@final
class ExperimentalWorkflowCpnMarkingDecoder:
    """Decode only the exact bounded canonical marking representation."""

    __slots__ = ()

    @property
    def profile_identity(
        self,
    ) -> ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity:
        return ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity(
            _MARKING_PROFILE
        )

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowCpnMarkingDecoder is not subclassable"
        )

    def decode(self, value: bytes) -> ColoredPetriNetMarking:
        """Return the exact marking represented by canonical ``value``."""
        parsed = _parse_canonical_payload(value)
        if (
            set(parsed) != {"marking", "schema"}
            or parsed.get("schema") != _MARKING_PROFILE
            or type(parsed.get("marking")) is not dict
        ):
            raise ValueError("marking representation has an invalid envelope")
        try:
            marking = _marking_from_state(parsed["marking"])
        except (
            KeyError,
            TypeError,
            ValueError,
            OverflowError,
            RecursionError,
        ) as exc:
            raise ValueError("marking representation is invalid") from exc
        if ExperimentalWorkflowCpnMarkingEncoder().encode(marking) != value:
            raise ValueError("marking representation is not canonical")
        return marking


def _parse_canonical_payload(value: bytes) -> dict[str, object]:
    if type(value) is not bytes:
        raise TypeError("marking representation must be bytes")
    if not value:
        raise ValueError("marking representation must not be empty")
    if len(value) > _MAX_MARKING_BYTES:
        raise ValueError("marking representation exceeds its byte bound")
    try:
        parsed = json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("marking representation must be UTF-8 JSON") from exc
    if type(parsed) is not dict:
        raise ValueError("marking representation must be a JSON object")
    try:
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (ValueError, UnicodeEncodeError) as exc:
        raise ValueError(
            "marking representation contains invalid JSON values"
        ) from exc
    if canonical != value:
        raise ValueError("marking representation must be canonical JSON")
    return parsed


def _marking_from_state(value: object) -> ColoredPetriNetMarking:
    state = _object(value, {"identity", "definition_identity", "places"})
    represented_places = state["places"]
    if type(represented_places) is not list:
        raise TypeError("marking places must be an array")
    if len(represented_places) > _MAX_ITEMS:
        raise ValueError("marking places exceed their count bound")
    total_tokens = 0
    places: list[ColoredPetriNetPlaceMarking] = []
    for represented_place in represented_places:
        place, token_count = _place_from_state(represented_place)
        total_tokens += token_count
        if total_tokens > _MAX_ITEMS:
            raise ValueError("marking tokens exceed their count bound")
        places.append(place)
    return ColoredPetriNetMarking(
        identity=ColoredPetriNetMarkingIdentity(_text(state["identity"])),
        definition_identity=ColoredPetriNetDefinitionIdentity(
            _text(state["definition_identity"])
        ),
        places=tuple(places),
    )


def _place_from_state(value: object) -> tuple[ColoredPetriNetPlaceMarking, int]:
    state = _object(value, {"place_identity", "tokens"})
    represented_tokens = state["tokens"]
    if type(represented_tokens) is not list:
        raise TypeError("place tokens must be an array")
    if len(represented_tokens) > _MAX_ITEMS:
        raise ValueError("place tokens exceed their count bound")
    tokens = tuple(_token_from_state(item) for item in represented_tokens)
    return (
        ColoredPetriNetPlaceMarking(
            place_identity=ColoredPetriNetPlaceIdentity(
                _text(state["place_identity"])
            ),
            tokens=tokens,
        ),
        len(tokens),
    )


def _token_from_state(value: object) -> ColoredPetriNetToken:
    state = _object(value, {"color_identity", "token_identity", "value"})
    represented_identity = state["token_identity"]
    return ColoredPetriNetToken(
        color_identity=ColoredPetriNetColorIdentity(
            _text(state["color_identity"])
        ),
        value=_value_from_state(state["value"]),
        token_identity=(
            None
            if represented_identity is None
            else ColoredPetriNetTokenIdentity(_text(represented_identity))
        ),
    )


__all__ = [
    "ExperimentalWorkflowCpnMarkingDecoder",
    "ExperimentalWorkflowCpnMarkingEncoder",
    "ExperimentalWorkflowCpnMarkingRepresentationProfileIdentity",
]
