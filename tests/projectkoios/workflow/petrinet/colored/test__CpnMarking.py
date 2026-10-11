r"""Software verification of ``CpnMarking``.

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

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnDefinitionIdentity,
    CpnPlaceIdentity,
)
from projectkoios.workflow.petrinet.colored.markings import (
    CpnMarking,
    CpnMarkingIdentity,
    CpnPlaceMarking,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnToken,
    CpnTokenIdentity,
    CpnValue,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = CpnMarking


def make_identified_token(identity: str) -> CpnToken:
    """Evidence ID: Owns no identifier; supports marking evidence.

    Requirement: Marking tests need one explicit individually correlated token.

    Acceptance: The helper returns a public token with the chosen nominal identity.
    """
    return CpnToken(
        CpnColorIdentity("color"),
        CpnValue(CpnValueKind.NONE, None),
        CpnTokenIdentity(identity),
    )


def make_marking(*places: CpnPlaceMarking) -> CpnMarking:
    """Evidence ID: Owns no identifier; supports marking evidence.

    Requirement: Tests need fixed nominal marking and definition identities.

    Acceptance: The helper returns a public marking containing supplied places.
    """
    return SUT(
        CpnMarkingIdentity("marking"),
        CpnDefinitionIdentity("definition"),
        places,
    )


def test_constructor__places__canonicalizes_representation_order() -> None:
    """Evidence ID: SV-PETRINET-029

    Requirement: Incidental place tuple order does not alter semantic marking state.

    Acceptance: Reversed input order produces equal markings stored by lexical nominal
    place identity.
    """
    a = CpnPlaceMarking(CpnPlaceIdentity("a"), ())
    b = CpnPlaceMarking(CpnPlaceIdentity("b"), ())
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
    place = CpnPlaceMarking(CpnPlaceIdentity("a"), ())
    with pytest.raises(ValueError):
        make_marking(place, place)


def test_constructor__token_identity__rejects_cross_place_duplication() -> None:
    """Evidence ID: SV-PETRINET-031

    Requirement: One individually correlated token cannot occupy multiple places in
    the same semantic marking.

    Acceptance: The duplicate nominal token identity raises ``ValueError`` exactly.
    """
    token = make_identified_token("token")
    a = CpnPlaceMarking(CpnPlaceIdentity("a"), (token,))
    b = CpnPlaceMarking(CpnPlaceIdentity("b"), (token,))
    with pytest.raises(ValueError):
        make_marking(a, b)


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(
            ("marking", CpnDefinitionIdentity("definition"), ()),
            id="lexical_marking_identity",
        ),
        pytest.param(
            (CpnMarkingIdentity("marking"), "definition", ()),
            id="lexical_definition_identity",
        ),
        pytest.param(
            (
                CpnMarkingIdentity("marking"),
                CpnDefinitionIdentity("definition"),
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
