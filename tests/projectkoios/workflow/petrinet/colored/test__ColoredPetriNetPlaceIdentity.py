r"""Software verification of ``ColoredPetriNetPlaceIdentity``.

Evidence profile: routine

Bounded artifact scope: one nominal generic colored-Petri-net identity DataObject.

Facet and represented meaning

The class represents one owner-local identity with a minimal lexical boundary.

Intrinsic and cross-object scope

Exact string preservation and rejection of empty or wrong-type values are covered.
Cross-object compatibility and wire encoding are excluded.

VVUQ and scientific exclusions

These synthetic checks establish software identity behavior only, not numerical or
scientific validity, UQ, authority, execution, or human acceptance.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetPlaceIdentity

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetPlaceIdentity


def test_constructor__identity_value__enforces_exact_lexical_boundary() -> None:
    """Evidence ID: SV-PETRINET-072

    Requirement: The nominal identity preserves a nonempty exact built-in string.

    Acceptance: A valid value is exact; empty and wrong-type values raise exactly.
    """
    assert SUT("identity").value == "identity"
    with pytest.raises(ValueError):
        SUT("")
    with pytest.raises(TypeError):
        SUT(1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        SUT(True)  # type: ignore[arg-type]
