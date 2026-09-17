r"""Software verification of ``ColoredPetriNetInputInscription``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetInputInscription`` generic
colored-Petri-net contract.

Facet and represented meaning

The class represents its documented immutable data or deterministic action boundary.

Intrinsic and cross-object scope

The focused class contract is covered; enablement and firing remain excluded.

VVUQ and scientific exclusions

These synthetic checks establish software behavior only, not numerical verification,
scientific validation, UQ, authority, execution, or human acceptance.
"""

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetColorIdentity,
    ColoredPetriNetInhibitorPattern,
    ColoredPetriNetInputInscription,
    ColoredPetriNetInputMode,
    ColoredPetriNetTokenPattern,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetInputInscription


def test_constructor__mode_and_patterns__preserves_multiplicity_and_types() -> None:
    """Evidence ID: SV-PETRINET-053

    Requirement: Consume/read use binding patterns and inhibit uses absence patterns.

    Acceptance: Repetition is retained while empty and mismatched modes reject.
    """
    color = ColoredPetriNetColorIdentity("color")
    token = ColoredPetriNetTokenPattern(
        ColoredPetriNetBindingVariableIdentity("x"), (color,)
    )
    inhibitor = ColoredPetriNetInhibitorPattern((color,))
    assert SUT(ColoredPetriNetInputMode.READ, (token, token)).patterns == (token, token)
    assert SUT(ColoredPetriNetInputMode.INHIBIT, (inhibitor,)).patterns == (inhibitor,)
    with pytest.raises(TypeError):
        SUT(ColoredPetriNetInputMode.INHIBIT, (token,))
    with pytest.raises(ValueError):
        SUT(ColoredPetriNetInputMode.CONSUME, ())
