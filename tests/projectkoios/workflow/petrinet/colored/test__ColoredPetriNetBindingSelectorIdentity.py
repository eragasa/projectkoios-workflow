r"""Software verification of ``ColoredPetriNetBindingSelectorIdentity``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetBindingSelectorIdentity`` contract.

Facet and represented meaning

Nominal identity of exact selector semantics.

Intrinsic and cross-object scope

The exact immutable lexical boundary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetBindingSelectorIdentity

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetBindingSelectorIdentity


def test_constructor__nominality__rejects_empty_and_wrong_types() -> None:
    """Evidence ID: SV-PETRINET-109

    Requirement: Selector identities are exact nonempty strings.

    Acceptance: Empty and non-string values raise documented exceptions.
    """
    with pytest.raises(ValueError):
        SUT("")
    with pytest.raises(TypeError):
        SUT(1)  # type: ignore[arg-type]
