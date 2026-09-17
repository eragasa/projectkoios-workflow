r"""Software verification of ``ColoredPetriNetToken``.

Evidence profile: routine

Bounded artifact scope: the color-qualified generic token DataObject.

Facet and represented meaning

The class represents one immutable color-qualified generic Petri-net value.

Intrinsic and cross-object scope

The tests cover nominal component typing, optional individual identity, exact
value semantics, immutability, and the absence of token-owned multiplicity.
Marking aggregation and Workflow result correlation remain outside this owner.

VVUQ and scientific exclusions

These synthetic checks establish only the software contract. They do not execute
simulations or establish numerical verification, scientific validation,
uncertainty quantification, or physical correctness.
"""

from dataclasses import FrozenInstanceError, fields

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetColorIdentity,
    ColoredPetriNetToken,
    ColoredPetriNetTokenIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = ColoredPetriNetToken


def make_value() -> ColoredPetriNetValue:
    """Evidence ID: Owns no identifier; supports token evidence in this module.

    Requirement: Token tests need one explicit valid generic value.

    Acceptance: The helper returns a public string-tagged synthetic value.
    """
    return ColoredPetriNetValue(ColoredPetriNetValueKind.STRING, "available")


def test_constructor__fields__preserves_anonymous_and_identified_tokens() -> None:
    """Evidence ID: SV-PETRINET-013

    Requirement: Tokens preserve exact nominal color, value, and optional identity.

    Acceptance: Anonymous and individually identified constructions retain all
    supplied components exactly.
    """
    color = ColoredPetriNetColorIdentity("color.available")
    value = make_value()
    identity = ColoredPetriNetTokenIdentity("token.1")
    anonymous = SUT(color, value)
    identified = SUT(color, value, identity)
    assert anonymous == SUT(color, value, None)
    assert anonymous.token_identity is None
    assert identified.token_identity is identity
    assert identified.color_identity is color
    assert identified.value is value


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"color_identity": "color"}, id="lexical_color_identity"),
        pytest.param({"value": "available"}, id="untagged_value"),
        pytest.param({"token_identity": "token"}, id="lexical_token_identity"),
    ],
)
def test_constructor__nominal_types__rejects_equal_looking_values(
    changes: dict[str, object],
) -> None:
    """Evidence ID: SV-PETRINET-014

    Requirement: Token components use their exact owner-local nominal types.

    Acceptance: Every named equal-looking non-nominal input raises ``TypeError``.
    """
    arguments: dict[str, object] = {
        "color_identity": ColoredPetriNetColorIdentity("color.available"),
        "value": make_value(),
        "token_identity": None,
    }
    arguments.update(changes)
    with pytest.raises(TypeError):
        SUT(**arguments)  # type: ignore[arg-type]


def test_constructor__field_inventory__omits_multiplicity() -> None:
    """Evidence ID: SV-PETRINET-015

    Requirement: A token has no multiplicity field; equal anonymous occurrences are
    counted only by their containing marking.

    Acceptance: The exact public dataclass field inventory contains only color,
    value, and optional identity.
    """
    assert tuple(field.name for field in fields(SUT)) == (
        "color_identity",
        "value",
        "token_identity",
    )


def test_constructor__immutability__produces_frozen_record() -> None:
    """Evidence ID: SV-PETRINET-016

    Requirement: Token state is operationally immutable.

    Acceptance: Assigning a public field raises ``FrozenInstanceError``.
    """
    token = SUT(ColoredPetriNetColorIdentity("color.available"), make_value())
    with pytest.raises(FrozenInstanceError):
        token.token_identity = ColoredPetriNetTokenIdentity("token.2")  # type: ignore[misc]
