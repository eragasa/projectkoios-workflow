"""Immutable generic colored-Petri-net multisets and transition bindings.

A place marking represents multiplicity by repeated equal anonymous tokens in a
canonical tuple. Tokens never carry counts. Individually identified tokens may
occur at most once in a complete marking. A transition binding is an ordered
sequence of variable/value assignments; its order is definition-owned and is
therefore preserved rather than lexically rewritten here.

The records perform no definition compatibility validation, enablement, firing,
persistence, Workflow orchestration, external effect, or scientific operation.
Their tests are software verification only.
"""

from dataclasses import dataclass
from typing import Any

from .values import (
    ColoredPetriNetToken,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)


@dataclass(frozen=True, slots=True)
class ColoredPetriNetDefinitionIdentity:
    """Nominal identity of one exact generic net definition.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity. Canonical encoding and wire
        derivation remain deferred.

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
            raise TypeError("definition identity value must be a string")
        if not self.value:
            raise ValueError("definition identity value must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetMarkingIdentity:
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
class ColoredPetriNetPlaceIdentity:
    """Nominal identity of one place in a generic net definition.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity.

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
            raise TypeError("place identity value must be a string")
        if not self.value:
            raise ValueError("place identity value must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetTransitionIdentity:
    """Nominal identity of one transition in a generic net definition.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity.

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
            raise TypeError("transition identity value must be a string")
        if not self.value:
            raise ValueError("transition identity value must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetBindingVariableIdentity:
    """Nominal identity of one variable in a transition binding.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity.

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
            raise TypeError("binding variable identity value must be a string")
        if not self.value:
            raise ValueError("binding variable identity value must not be empty")


def _value_order_key(value: ColoredPetriNetValue) -> tuple[str, Any]:
    """Return a deterministic in-memory key for one closed tagged value."""
    active = value.value
    if value.kind is ColoredPetriNetValueKind.NONE:
        return (value.kind.value, ())
    return (value.kind.value, active)


def _token_order_key(token: ColoredPetriNetToken) -> tuple[Any, ...]:
    """Return the contract's deterministic in-memory token ordering key."""
    identity = token.token_identity
    return (
        token.color_identity.value,
        *_value_order_key(token.value),
        identity is not None,
        "" if identity is None else identity.value,
    )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetPlaceMarking:
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

    place_identity: ColoredPetriNetPlaceIdentity
    tokens: tuple[ColoredPetriNetToken, ...]

    def __post_init__(self) -> None:
        """Validate and canonicalize the owned semantic multiset."""
        if type(self.place_identity) is not ColoredPetriNetPlaceIdentity:
            raise TypeError("place_identity must be ColoredPetriNetPlaceIdentity")
        if type(self.tokens) is not tuple or any(
            type(token) is not ColoredPetriNetToken for token in self.tokens
        ):
            raise TypeError("tokens must be a tuple of ColoredPetriNetToken")
        identities = tuple(
            token.token_identity
            for token in self.tokens
            if token.token_identity is not None
        )
        if len(set(identities)) != len(identities):
            raise ValueError("identified token identities must be unique at a place")
        object.__setattr__(
            self, "tokens", tuple(sorted(self.tokens, key=_token_order_key))
        )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetMarking:
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

    identity: ColoredPetriNetMarkingIdentity
    definition_identity: ColoredPetriNetDefinitionIdentity
    places: tuple[ColoredPetriNetPlaceMarking, ...]

    def __post_init__(self) -> None:
        """Validate complete owned state and canonicalize place order."""
        if type(self.identity) is not ColoredPetriNetMarkingIdentity:
            raise TypeError("identity must be ColoredPetriNetMarkingIdentity")
        if type(self.definition_identity) is not ColoredPetriNetDefinitionIdentity:
            raise TypeError(
                "definition_identity must be ColoredPetriNetDefinitionIdentity"
            )
        if type(self.places) is not tuple or any(
            type(place) is not ColoredPetriNetPlaceMarking for place in self.places
        ):
            raise TypeError("places must be a tuple of ColoredPetriNetPlaceMarking")
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
        object.__setattr__(
            self,
            "places",
            tuple(sorted(self.places, key=lambda place: place.place_identity.value)),
        )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetBindingAssignment:
    """Association of one definition-owned variable with one generic value.

    Parameters
    ----------
    variable_identity
        Nominal identity of the bound variable.
    value
        Exact immutable generic value assigned to the variable.

    Raises
    ------
    TypeError
        A field does not have its exact owner-local nominal type.
    """

    variable_identity: ColoredPetriNetBindingVariableIdentity
    value: ColoredPetriNetValue

    def __post_init__(self) -> None:
        """Validate exact nominal assignment components."""
        if type(self.variable_identity) is not ColoredPetriNetBindingVariableIdentity:
            raise TypeError(
                "variable_identity must be ColoredPetriNetBindingVariableIdentity"
            )
        if type(self.value) is not ColoredPetriNetValue:
            raise TypeError("value must be ColoredPetriNetValue")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetBinding:
    """One immutable ordered variable/value binding for a transition.

    Parameters
    ----------
    transition_identity
        Nominal identity of the transition for which values are bound.
    assignments
        Complete variable/value assignments in the owning definition's declared
        variable order. This DataObject preserves that order and requires unique
        variable identities; it does not infer or lexically reorder policy.

    Raises
    ------
    TypeError
        A field has the wrong nominal type or ``assignments`` is mutable.
    ValueError
        A variable identity occurs more than once.
    """

    transition_identity: ColoredPetriNetTransitionIdentity
    assignments: tuple[ColoredPetriNetBindingAssignment, ...]

    def __post_init__(self) -> None:
        """Validate the intrinsic ordered-binding structure."""
        if type(self.transition_identity) is not ColoredPetriNetTransitionIdentity:
            raise TypeError(
                "transition_identity must be ColoredPetriNetTransitionIdentity"
            )
        if type(self.assignments) is not tuple or any(
            type(item) is not ColoredPetriNetBindingAssignment
            for item in self.assignments
        ):
            raise TypeError(
                "assignments must be a tuple of ColoredPetriNetBindingAssignment"
            )
        variables = tuple(item.variable_identity for item in self.assignments)
        if len(set(variables)) != len(variables):
            raise ValueError("binding variable identities must be unique")
