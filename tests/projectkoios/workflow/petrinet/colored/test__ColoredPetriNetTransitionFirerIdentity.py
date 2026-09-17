r"""Software verification of ``ColoredPetriNetTransitionFirerIdentity``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetTransitionFirerIdentity`` contract.

Facet and represented meaning

Nominal identity of exact pure-firing semantics.

Intrinsic and cross-object scope

The exact immutable lexical boundary is covered.

VVUQ and scientific exclusions

This is software verification, not external execution or scientific validation.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetTransitionFirerIdentity

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetTransitionFirerIdentity


def test_constructor__nominality__rejects_empty_and_wrong_types() -> None:
    """Evidence ID: SV-PETRINET-130

    Requirement: Firer identities are exact nonempty strings.

    Acceptance: Empty and non-string values raise documented exceptions.
    """
    with pytest.raises(ValueError):
        SUT("")
    with pytest.raises(TypeError):
        SUT(1)  # type: ignore[arg-type]
