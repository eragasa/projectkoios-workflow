r"""Software verification of ``ColoredPetriNetColorIdentity``.

Evidence profile: routine

Bounded artifact scope: the nominal color-identity DataObject.

Facet and represented meaning

The class represents one nominal owner-local generic color identity.

Intrinsic and cross-object scope

Construction, exact type boundaries, value invariants, and immutability are
intrinsic. No definition compatibility or cross-object policy is exercised.

VVUQ and scientific exclusions

These synthetic checks establish only the documented software contract, not
numerical verification, scientific validation, uncertainty quantification, or
physical meaning.
"""

from dataclasses import FrozenInstanceError

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetColorIdentity

pytestmark = pytest.mark.software_verification

SUT = ColoredPetriNetColorIdentity


def test_constructor__fields__preserves_nonempty_exact_string() -> None:
    """Evidence ID: SV-PETRINET-001

    Requirement: A color identity preserves its exact nonempty string value.

    Acceptance: Construction stores the exact supplied value.
    """
    assert SUT("color.alpha").value == "color.alpha"


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(None, id="none"),
        pytest.param(1, id="integer"),
        pytest.param(True, id="boolean"),
    ],
)
def test_constructor__semantic_types__rejects_non_strings(value: object) -> None:
    """Evidence ID: SV-PETRINET-002

    Requirement: Color identity values accept only exact built-in strings.

    Acceptance: Every named wrong-type partition raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT(value)  # type: ignore[arg-type]


def test_constructor__value_invariants__rejects_empty_string() -> None:
    """Evidence ID: SV-PETRINET-003

    Requirement: A color identity must not be empty.

    Acceptance: The empty string raises ``ValueError`` exactly.
    """
    with pytest.raises(ValueError):
        SUT("")


def test_constructor__immutability__produces_frozen_record() -> None:
    """Evidence ID: SV-PETRINET-004

    Requirement: A color identity is operationally immutable.

    Acceptance: Assigning its public field raises ``FrozenInstanceError``.
    """
    identity = SUT("color.alpha")
    with pytest.raises(FrozenInstanceError):
        identity.value = "color.beta"  # type: ignore[misc]
