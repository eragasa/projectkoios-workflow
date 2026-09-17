r"""Software verification of ``ColoredPetriNetTokenIdentity``.

Evidence profile: routine

Bounded artifact scope: the nominal token-identity DataObject.

Facet and represented meaning

The class represents one nominal owner-local generic token identity.

Intrinsic and cross-object scope

Construction, exact type boundaries, value invariants, and nominal separation
are intrinsic. No marking or Workflow correlation policy is exercised.

VVUQ and scientific exclusions

These synthetic checks establish only the documented software contract, not
numerical verification, scientific validation, uncertainty quantification, or
physical meaning.
"""

from dataclasses import FrozenInstanceError

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetColorIdentity,
    ColoredPetriNetTokenIdentity,
)

pytestmark = pytest.mark.software_verification

SUT = ColoredPetriNetTokenIdentity


def test_constructor__fields__preserves_nonempty_exact_string() -> None:
    """Evidence ID: SV-PETRINET-005

    Requirement: A token identity preserves its exact nonempty string value.

    Acceptance: Construction stores the exact supplied value.
    """
    assert SUT("token.alpha").value == "token.alpha"


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(None, id="none"),
        pytest.param(1, id="integer"),
        pytest.param(True, id="boolean"),
    ],
)
def test_constructor__semantic_types__rejects_non_strings(value: object) -> None:
    """Evidence ID: SV-PETRINET-006

    Requirement: Token identity values accept only exact built-in strings.

    Acceptance: Every named wrong-type partition raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT(value)  # type: ignore[arg-type]


def test_constructor__value_invariants__rejects_empty_string() -> None:
    """Evidence ID: SV-PETRINET-007

    Requirement: A token identity must not be empty.

    Acceptance: The empty string raises ``ValueError`` exactly.
    """
    with pytest.raises(ValueError):
        SUT("")


def test_constructor__immutability__produces_frozen_record() -> None:
    """Evidence ID: SV-PETRINET-019

    Requirement: A token identity is operationally immutable.

    Acceptance: Assigning its public field raises ``FrozenInstanceError``.
    """
    identity = SUT("token.alpha")
    with pytest.raises(FrozenInstanceError):
        identity.value = "token.beta"  # type: ignore[misc]


def test_method__eq__rejects_equal_looking_color_identity() -> None:
    """Evidence ID: SV-PETRINET-008

    Requirement: Token and color identities remain nominally distinct.

    Acceptance: Equal lexical values in the two identity classes are unequal.
    """
    assert SUT("shared") != ColoredPetriNetColorIdentity("shared")
