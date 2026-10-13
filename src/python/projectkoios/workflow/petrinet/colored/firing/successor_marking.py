"""Pure successor-marking construction from audited firing effects."""

from __future__ import annotations
import json
from dataclasses import dataclass
from hashlib import sha256
from typing import final
from ..control.records.values.canonicalization import (
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from ..definitions import CpnPlaceIdentity
from ..markings import CpnMarking, CpnMarkingIdentity, CpnPlaceMarking
from ..values import CpnToken
from .audits import CpnFiringAudit
from .inputs import CpnFiringInput


@dataclass(frozen=True, slots=True)
class CpnSuccessorMarkingBuildingRequest:
    """One firing input and complete audit requested as a successor marking."""

    firing_input: CpnFiringInput
    audit: CpnFiringAudit

    def __post_init__(self) -> None:
        if type(self.firing_input) is not CpnFiringInput:
            raise TypeError("firing_input must be CpnFiringInput")
        if type(self.audit) is not CpnFiringAudit:
            raise TypeError("audit must be CpnFiringAudit")


@dataclass(frozen=True, slots=True)
class CpnSuccessorMarkingBuilderIdentity:
    """Identity of exact successor-marking construction semantics."""

    value: str = "projectkoios.workflow.cpn.successor-marking-builder:0.1"


@final
class CpnSuccessorMarkingBuilder:
    """Construct one content-identified successor from retained firing evidence."""

    __slots__ = ()

    @property
    def identity(self) -> CpnSuccessorMarkingBuilderIdentity:
        """Return exact successor-building semantics identity."""
        return CpnSuccessorMarkingBuilderIdentity()

    def execute(
        self, request: CpnSuccessorMarkingBuildingRequest
    ) -> CpnMarking:
        """Return the exact successor marking represented by the audit."""
        if type(request) is not CpnSuccessorMarkingBuildingRequest:
            raise TypeError(
                "request must be CpnSuccessorMarkingBuildingRequest"
            )
        firing_input = request.firing_input
        audit = request.audit
        consumed = {
            (item.place_identity, item.occurrence_ordinal)
            for item in audit.consumed_occurrences
        }
        produced_by_place: dict[CpnPlaceIdentity, list[CpnToken]] = {}
        for item in audit.produced_tokens:
            produced_by_place.setdefault(item.place_identity, []).append(
                item.token
            )
        places = tuple(
            CpnPlaceMarking(
                place.place_identity,
                tuple(
                    token
                    for ordinal, token in enumerate(place.tokens)
                    if (place.place_identity, ordinal) not in consumed
                )
                + tuple(produced_by_place.get(place.place_identity, ())),
            )
            for place in firing_input.predecessor_marking.places
        )
        represented_places = []
        for place in places:
            represented_tokens = []
            for token in place.tokens:
                represented_tokens.append(
                    {
                        "color": token.color_identity.value,
                        "kind": token.value.kind.value,
                        "value": json.loads(
                            CpnValueCanonicalizer()
                            .execute(CpnValueCanonicalizationInput(token.value))
                            .canonical_bytes
                        ),
                        "identity": (
                            None
                            if token.token_identity is None
                            else token.token_identity.value
                        ),
                    }
                )
            represented_places.append(
                {
                    "place": place.place_identity.value,
                    "tokens": represented_tokens,
                }
            )
        encoded = json.dumps(
            {
                "domain": "projectkoios.workflow.cpn.successor-marking:0.1",
                "definition": firing_input.definition.identity.value,
                "predecessor": firing_input.predecessor_marking.identity.value,
                "places": represented_places,
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return CpnMarking(
            CpnMarkingIdentity(sha256(encoded).hexdigest()),
            firing_input.definition.identity,
            places,
        )
