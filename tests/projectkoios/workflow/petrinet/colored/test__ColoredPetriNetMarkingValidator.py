r"""Software verification of ``ColoredPetriNetMarkingValidator``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetMarkingValidator`` generic
colored-Petri-net contract.

Facet and represented meaning

The class represents its documented immutable data or deterministic action boundary.

Intrinsic and cross-object scope

The focused class contract is covered; enablement and firing remain excluded.

VVUQ and scientific exclusions

These synthetic checks establish software behavior only, not numerical verification,
scientific validation, UQ, authority, execution, or human acceptance.
"""

from dataclasses import replace

import pytest
from _validation_fixtures import valid_definition

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetColorDefinition,
    ColoredPetriNetColorIdentity,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetMarking,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetMarkingValidator,
    ColoredPetriNetPlaceDefinition,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetPlaceMarking,
    ColoredPetriNetToken,
    ColoredPetriNetValidationIssueCode,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetMarkingValidator


def test_method__execute__accepts_anonymous_multiplicity() -> None:
    """Evidence ID: SV-PETRINET-069

    Requirement: Equal anonymous tokens represent valid marking-owned multiplicity.

    Acceptance: Two compatible equal tokens return the exact empty issue tuple.
    """
    definition = valid_definition()
    token = ColoredPetriNetToken(
        definition.colors[0].identity,
        ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 1),
    )
    marking = ColoredPetriNetMarking(
        ColoredPetriNetMarkingIdentity("marking"),
        definition.identity,
        (ColoredPetriNetPlaceMarking(definition.places[0].identity, (token, token)),),
    )
    assert SUT().execute(definition, marking).issues == ()


def test_method__execute__returns_exact_ordered_relationship_findings() -> None:
    """Evidence ID: SV-PETRINET-070

    Requirement: Validation reports identity, place, color, and value-kind defects.

    Acceptance: Exact canonical paths, codes, related identities, and messages equal
    the fixed complete oracle.
    """
    definition = valid_definition()
    wrong_kind = ColoredPetriNetToken(
        definition.colors[0].identity,
        ColoredPetriNetValue(ColoredPetriNetValueKind.STRING, "wrong"),
    )
    unknown = ColoredPetriNetToken(
        ColoredPetriNetColorIdentity("unknown"),
        ColoredPetriNetValue(ColoredPetriNetValueKind.NONE, None),
    )
    marking = ColoredPetriNetMarking(
        ColoredPetriNetMarkingIdentity("marking"),
        ColoredPetriNetDefinitionIdentity("other-definition"),
        (
            ColoredPetriNetPlaceMarking(definition.places[0].identity, (wrong_kind,)),
            ColoredPetriNetPlaceMarking(
                ColoredPetriNetPlaceIdentity("extra"), (unknown,)
            ),
        ),
    )
    assert tuple(
        (item.path, item.code, item.related_identities, item.message)
        for item in SUT().execute(definition, marking).issues
    ) == (
        (
            ("marking", "definition_identity"),
            ColoredPetriNetValidationIssueCode.DEFINITION_IDENTITY_MISMATCH,
            ("definition", "other-definition"),
            "marking and supplied definition identities differ",
        ),
        (
            ("marking", "places"),
            ColoredPetriNetValidationIssueCode.PLACE_SET_MISMATCH,
            ("extra",),
            "marking place set differs from definition place set",
        ),
        (
            ("marking", "places", "extra", "tokens", "0", "color"),
            ColoredPetriNetValidationIssueCode.UNKNOWN_COLOR,
            ("unknown",),
            "token references an unknown color",
        ),
        (
            ("marking", "places", "place", "tokens", "0", "value_kind"),
            ColoredPetriNetValidationIssueCode.VALUE_KIND_NOT_ALLOWED,
            ("number", "string"),
            "token value kind is not admitted by its color",
        ),
    )


def test_method__execute__retains_equal_nominal_spellings() -> None:
    """Evidence ID: SV-PETRINET-088

    Requirement: Distinct nominal place and color identities may share lexical text
    without making validation partial.

    Acceptance: The color-not-allowed finding retains both equal spellings.
    """
    base = valid_definition()
    same_color = ColoredPetriNetColorDefinition(
        ColoredPetriNetColorIdentity("same"), (ColoredPetriNetValueKind.NONE,)
    )
    admitted = ColoredPetriNetColorDefinition(
        ColoredPetriNetColorIdentity("admitted"), (ColoredPetriNetValueKind.NONE,)
    )
    same_place = ColoredPetriNetPlaceDefinition(
        ColoredPetriNetPlaceIdentity("same"), (admitted.identity,)
    )
    definition = replace(base, colors=(same_color, admitted), places=(same_place,))
    token = ColoredPetriNetToken(
        same_color.identity,
        ColoredPetriNetValue(ColoredPetriNetValueKind.NONE, None),
    )
    marking = ColoredPetriNetMarking(
        ColoredPetriNetMarkingIdentity("marking"),
        definition.identity,
        (ColoredPetriNetPlaceMarking(same_place.identity, (token,)),),
    )
    result = SUT().execute(definition, marking)
    assert tuple(
        (item.path, item.code, item.related_identities, item.message)
        for item in result.issues
    ) == (
        (
            ("marking", "places", "same", "tokens", "0", "color"),
            ColoredPetriNetValidationIssueCode.COLOR_NOT_ALLOWED,
            ("same", "same"),
            "token color is not admitted by the place",
        ),
    )


def test_method__execute__rejects_wrong_nominal_types() -> None:
    """Evidence ID: SV-PETRINET-089

    Requirement: Marking validation accepts exact public definition and marking types.

    Acceptance: Each equal-looking wrong-type argument raises ``TypeError`` exactly.
    """
    definition = valid_definition()
    marking = ColoredPetriNetMarking(
        ColoredPetriNetMarkingIdentity("marking"), definition.identity, ()
    )
    with pytest.raises(TypeError):
        SUT().execute("definition", marking)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        SUT().execute(definition, "marking")  # type: ignore[arg-type]
