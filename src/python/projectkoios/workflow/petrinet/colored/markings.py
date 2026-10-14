"""Immutable generic colored-Petri-net markings and place multisets."""

from dataclasses import dataclass
from typing import final

from .control.records.ordering import (
    CpnValueOrderingInput,
    CpnValueOrderingPolicy,
)
from .definitions import CpnDefinitionIdentity, CpnPlaceIdentity
from .values import CpnToken


@dataclass(frozen=True, slots=True)
class CpnMarkingIdentity:
    """Nominal identity of one exact semantic generic marking.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity. This in-memory contract does not
        select a digest, canonical wire, or revision scheme.

    Raises
    ------
    TypeError
        ``value`` is not an exact built-in string.
    ValueError
        ``value`` is empty.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the exact built-in nonempty string boundary."""
        if type(self.value) is not str:
            raise TypeError("marking identity value must be a string")
        if not self.value:
            raise ValueError("marking identity value must not be empty")


@dataclass(frozen=True, slots=True)
class CpnTokenOrderingInput:
    """One immutable token sequence requested for semantic ordering."""

    tokens: tuple[CpnToken, ...]

    def __post_init__(self) -> None:
        if type(self.tokens) is not tuple or any(
            type(item) is not CpnToken for item in self.tokens
        ):
            raise TypeError("tokens must contain exact CpnToken values")


@dataclass(frozen=True, slots=True)
class CpnTokenOrderingResult:
    """One deterministically ordered immutable token sequence."""

    tokens: tuple[CpnToken, ...]

    def __post_init__(self) -> None:
        if type(self.tokens) is not tuple or any(
            type(item) is not CpnToken for item in self.tokens
        ):
            raise TypeError("tokens must contain exact CpnToken values")


@dataclass(frozen=True, slots=True)
class CpnTokenOrderingPolicyIdentity:
    """Identity of exact generic token-ordering semantics."""

    value: str = "projectkoios.workflow.cpn.token-ordering-policy:0.1"


@final
class CpnTokenOrderingPolicy:
    """Order tokens by color, admitted value order, and token identity."""

    __slots__ = ()

    @property
    def identity(self) -> CpnTokenOrderingPolicyIdentity:
        """Return exact token-ordering semantics identity."""
        return CpnTokenOrderingPolicyIdentity()

    def execute(
        self, ordering_input: CpnTokenOrderingInput
    ) -> CpnTokenOrderingResult:
        """Return a stable total ordering without hidden key functions."""
        if type(ordering_input) is not CpnTokenOrderingInput:
            raise TypeError("ordering_input must be CpnTokenOrderingInput")
        ordered: list[tuple[tuple[object, ...], int, CpnToken]] = []
        for ordinal, token in enumerate(ordering_input.tokens):
            identity = token.token_identity
            key = (
                token.color_identity.value,
                *CpnValueOrderingPolicy()
                .execute(CpnValueOrderingInput(token.value))
                .key,
                identity is not None,
                "" if identity is None else identity.value,
            )
            ordered.append((key, ordinal, token))
        ordered.sort()
        return CpnTokenOrderingResult(tuple(item[2] for item in ordered))


@dataclass(frozen=True, slots=True)
class CpnPlaceMarking:
    """Immutable semantic token multiset at one generic place.

    Parameters
    ----------
    place_identity
        Nominal identity of the represented place.
    tokens
        Tuple-backed token multiset. Repeated equal anonymous tokens represent
        multiplicity and are retained. An individually identified token may occur
        only once at this place. Input order is canonicalized by generic token
        semantics rather than caller order.

    Raises
    ------
    TypeError
        A field has the wrong nominal type or ``tokens`` is mutable.
    ValueError
        One individual token identity occurs more than once.
    """

    place_identity: CpnPlaceIdentity
    tokens: tuple[CpnToken, ...]

    def __post_init__(self) -> None:
        """Validate and canonicalize the owned semantic multiset."""
        if type(self.place_identity) is not CpnPlaceIdentity:
            raise TypeError("place_identity must be CpnPlaceIdentity")
        if type(self.tokens) is not tuple or any(
            type(token) is not CpnToken for token in self.tokens
        ):
            raise TypeError("tokens must be a tuple of CpnToken")
        identities = tuple(
            token.token_identity
            for token in self.tokens
            if token.token_identity is not None
        )
        if len(set(identities)) != len(identities):
            raise ValueError(
                "identified token identities must be unique at a place"
            )
        ordered = CpnTokenOrderingPolicy().execute(
            CpnTokenOrderingInput(self.tokens)
        )
        object.__setattr__(self, "tokens", ordered.tokens)


@dataclass(frozen=True, slots=True)
class CpnMarking:
    """One complete immutable semantic marking for an exact net definition.

    Parameters
    ----------
    identity
        Nominal identity of this exact semantic marking.
    definition_identity
        Exact generic definition under which the marking is interpreted.
    places
        Unique place markings, including empty places when the definition requires
        them, stored in canonical place-identity order.

    Raises
    ------
    TypeError
        A field has the wrong nominal type or ``places`` is mutable.
    ValueError
        Place identities are duplicated or one individual token identity occurs in
        more than one place.

    Notes
    -----
    Completeness against a definition is cross-object validation and belongs to a
    later validator. Revision and wire-schema state are deliberately absent.
    """

    identity: CpnMarkingIdentity
    definition_identity: CpnDefinitionIdentity
    places: tuple[CpnPlaceMarking, ...]

    def __post_init__(self) -> None:
        """Validate complete owned state and canonicalize place order."""
        if type(self.identity) is not CpnMarkingIdentity:
            raise TypeError("identity must be CpnMarkingIdentity")
        if type(self.definition_identity) is not CpnDefinitionIdentity:
            raise TypeError("definition_identity must be CpnDefinitionIdentity")
        if type(self.places) is not tuple or any(
            type(place) is not CpnPlaceMarking for place in self.places
        ):
            raise TypeError("places must be a tuple of CpnPlaceMarking")
        place_ids = tuple(place.place_identity for place in self.places)
        if len(set(place_ids)) != len(place_ids):
            raise ValueError("place identities must be unique")
        token_ids = tuple(
            token.token_identity
            for place in self.places
            for token in place.tokens
            if token.token_identity is not None
        )
        if len(set(token_ids)) != len(token_ids):
            raise ValueError(
                "identified token identities must be unique across the marking"
            )
        ordered_places = [
            (place.place_identity.value, ordinal, place)
            for ordinal, place in enumerate(self.places)
        ]
        ordered_places.sort()
        object.__setattr__(
            self,
            "places",
            tuple(item[2] for item in ordered_places),
        )
