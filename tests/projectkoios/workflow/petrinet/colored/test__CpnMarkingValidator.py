r"""Software verification of ``CpnMarkingValidator``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnMarkingValidator`` generic
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

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnColorDefinition,
    CpnDefinitionIdentity,
    CpnPlaceDefinition,
    CpnPlaceIdentity,
)
from projectkoios.workflow.petrinet.colored.markings import (
    CpnMarking,
    CpnMarkingIdentity,
    CpnPlaceMarking,
)
from projectkoios.workflow.petrinet.colored.validation.findings import (
    CpnValidationIssueCode,
)
from projectkoios.workflow.petrinet.colored.validation.markings import (
    CpnMarkingValidationInput,
    CpnMarkingValidator,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnToken,
    CpnValue,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = CpnMarkingValidator


def test_method__execute__accepts_anonymous_multiplicity() -> None:
    """Evidence ID: SV-PETRINET-069

    Requirement: Equal anonymous tokens represent valid marking-owned multiplicity.

    Acceptance: Two compatible equal tokens return the exact empty issue tuple.
    """
    definition = valid_definition()
    token = CpnToken(
        definition.colors[0].identity,
        CpnValue(CpnValueKind.INTEGER, 1),
    )
    marking = CpnMarking(
        CpnMarkingIdentity("marking"),
        definition.identity,
        (CpnPlaceMarking(definition.places[0].identity, (token, token)),),
    )
    assert (
        SUT().execute(CpnMarkingValidationInput(definition, marking)).issues
        == ()
    )


def test_method__execute__returns_exact_ordered_relationship_findings() -> None:
    """Evidence ID: SV-PETRINET-070

    Requirement: Validation reports identity, place, color, and value-kind defects.

    Acceptance: Exact canonical paths, codes, related identities, and messages equal
    the fixed complete oracle.
    """
    definition = valid_definition()
    wrong_kind = CpnToken(
        definition.colors[0].identity,
        CpnValue(CpnValueKind.STRING, "wrong"),
    )
    unknown = CpnToken(
        CpnColorIdentity("unknown"),
        CpnValue(CpnValueKind.NONE, None),
    )
    marking = CpnMarking(
        CpnMarkingIdentity("marking"),
        CpnDefinitionIdentity("other-definition"),
        (
            CpnPlaceMarking(definition.places[0].identity, (wrong_kind,)),
            CpnPlaceMarking(CpnPlaceIdentity("extra"), (unknown,)),
        ),
    )
    assert tuple(
        (item.path, item.code, item.related_identities, item.message)
        for item in SUT()
        .execute(CpnMarkingValidationInput(definition, marking))
        .issues
    ) == (
        (
            ("marking", "definition_identity"),
            CpnValidationIssueCode.DEFINITION_IDENTITY_MISMATCH,
            ("definition", "other-definition"),
            "marking and supplied definition identities differ",
        ),
        (
            ("marking", "places"),
            CpnValidationIssueCode.PLACE_SET_MISMATCH,
            ("extra",),
            "marking place set differs from definition place set",
        ),
        (
            ("marking", "places", "extra", "tokens", "0", "color"),
            CpnValidationIssueCode.UNKNOWN_COLOR,
            ("unknown",),
            "token references an unknown color",
        ),
        (
            ("marking", "places", "place", "tokens", "0", "value_kind"),
            CpnValidationIssueCode.VALUE_KIND_NOT_ALLOWED,
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
    same_color = CpnColorDefinition(
        CpnColorIdentity("same"), (CpnValueKind.NONE,)
    )
    admitted = CpnColorDefinition(
        CpnColorIdentity("admitted"), (CpnValueKind.NONE,)
    )
    same_place = CpnPlaceDefinition(
        CpnPlaceIdentity("same"), (admitted.identity,)
    )
    definition = replace(
        base, colors=(same_color, admitted), places=(same_place,)
    )
    token = CpnToken(
        same_color.identity,
        CpnValue(CpnValueKind.NONE, None),
    )
    marking = CpnMarking(
        CpnMarkingIdentity("marking"),
        definition.identity,
        (CpnPlaceMarking(same_place.identity, (token,)),),
    )
    result = SUT().execute(CpnMarkingValidationInput(definition, marking))
    assert tuple(
        (item.path, item.code, item.related_identities, item.message)
        for item in result.issues
    ) == (
        (
            ("marking", "places", "same", "tokens", "0", "color"),
            CpnValidationIssueCode.COLOR_NOT_ALLOWED,
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
    marking = CpnMarking(CpnMarkingIdentity("marking"), definition.identity, ())
    with pytest.raises(TypeError, match="validation_input"):
        SUT().execute("request")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="definition"):
        CpnMarkingValidationInput("definition", marking)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="marking"):
        CpnMarkingValidationInput(definition, "marking")  # type: ignore[arg-type]
