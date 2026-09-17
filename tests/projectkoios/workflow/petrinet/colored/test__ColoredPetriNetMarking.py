r"""Software verification of ``ColoredPetriNetMarking``.

Evidence profile: routine

Bounded artifact scope: one complete immutable semantic generic marking.

Facet and represented meaning

The class binds exact marking and definition identities to unique canonically ordered
place multisets.

Intrinsic and cross-object scope

Place uniqueness, cross-place identified-token uniqueness, nominal typing, ordering,
and immutability are covered. Completeness against a definition is excluded.

VVUQ and scientific exclusions

These synthetic checks establish software aggregate behavior only, not numerical
verification, scientific validation, uncertainty quantification, or simulation state.
"""

from dataclasses import FrozenInstanceError

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetColorIdentity,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetMarking,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetPlaceMarking,
    ColoredPetriNetToken,
    ColoredPetriNetTokenIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = ColoredPetriNetMarking


def make_identified_token(identity: str) -> ColoredPetriNetToken:
    """Evidence ID: Owns no identifier; supports marking evidence.

    Requirement: Marking tests need one explicit individually correlated token.

    Acceptance: The helper returns a public token with the chosen nominal identity.
    """
    return ColoredPetriNetToken(
        ColoredPetriNetColorIdentity("color"),
        ColoredPetriNetValue(ColoredPetriNetValueKind.NONE, None),
        ColoredPetriNetTokenIdentity(identity),
    )


def make_marking(*places: ColoredPetriNetPlaceMarking) -> ColoredPetriNetMarking:
    """Evidence ID: Owns no identifier; supports marking evidence.

    Requirement: Tests need fixed nominal marking and definition identities.

    Acceptance: The helper returns a public marking containing supplied places.
    """
    return SUT(
        ColoredPetriNetMarkingIdentity("marking"),
        ColoredPetriNetDefinitionIdentity("definition"),
        places,
    )


def test_constructor__places__canonicalizes_representation_order() -> None:
    """Evidence ID: SV-PETRINET-029

    Requirement: Incidental place tuple order does not alter semantic marking state.

    Acceptance: Reversed input order produces equal markings stored by lexical nominal
    place identity.
    """
    a = ColoredPetriNetPlaceMarking(ColoredPetriNetPlaceIdentity("a"), ())
    b = ColoredPetriNetPlaceMarking(ColoredPetriNetPlaceIdentity("b"), ())
    assert make_marking(b, a) == make_marking(a, b)
    assert make_marking(b, a).places == (a, b)


def test_constructor__immutability__produces_frozen_record() -> None:
    """Evidence ID: SV-PETRINET-040

    Requirement: A complete marking is operationally immutable.

    Acceptance: Assigning its place tuple raises ``FrozenInstanceError``.
    """
    marking = make_marking()
    with pytest.raises(FrozenInstanceError):
        marking.places = ()  # type: ignore[misc]


def test_constructor__place_identity__rejects_duplicate_places() -> None:
    """Evidence ID: SV-PETRINET-030

    Requirement: A complete marking contains at most one multiset for each place.

    Acceptance: Repeating a nominal place identity raises ``ValueError`` exactly.
    """
    place = ColoredPetriNetPlaceMarking(ColoredPetriNetPlaceIdentity("a"), ())
    with pytest.raises(ValueError):
        make_marking(place, place)


def test_constructor__token_identity__rejects_cross_place_duplication() -> None:
    """Evidence ID: SV-PETRINET-031

    Requirement: One individually correlated token cannot occupy multiple places in
    the same semantic marking.

    Acceptance: The duplicate nominal token identity raises ``ValueError`` exactly.
    """
    token = make_identified_token("token")
    a = ColoredPetriNetPlaceMarking(ColoredPetriNetPlaceIdentity("a"), (token,))
    b = ColoredPetriNetPlaceMarking(ColoredPetriNetPlaceIdentity("b"), (token,))
    with pytest.raises(ValueError):
        make_marking(a, b)


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(
            ("marking", ColoredPetriNetDefinitionIdentity("definition"), ()),
            id="lexical_marking_identity",
        ),
        pytest.param(
            (ColoredPetriNetMarkingIdentity("marking"), "definition", ()),
            id="lexical_definition_identity",
        ),
        pytest.param(
            (
                ColoredPetriNetMarkingIdentity("marking"),
                ColoredPetriNetDefinitionIdentity("definition"),
                [],
            ),
            id="mutable_place_collection",
        ),
    ],
)
def test_constructor__nominal_types__rejects_wrong_types(
    arguments: tuple[object, object, object],
) -> None:
    """Evidence ID: SV-PETRINET-032

    Requirement: Markings accept exact nominal identities and immutable place tuples.

    Acceptance: Every named wrong-type partition raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT(*arguments)  # type: ignore[arg-type]
