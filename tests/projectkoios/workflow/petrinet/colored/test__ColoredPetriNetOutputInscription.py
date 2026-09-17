r"""Software verification of ``ColoredPetriNetOutputInscription``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetOutputInscription`` generic
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
    ColoredPetriNetColorIdentity,
    ColoredPetriNetOutputInscription,
    ColoredPetriNetTokenTemplate,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetOutputInscription


def test_constructor__templates__preserves_nonempty_order() -> None:
    """Evidence ID: SV-PETRINET-054

    Requirement: Output inscriptions preserve nonempty ordered template multiplicity.

    Acceptance: Two templates remain ordered; empty and mutable inputs reject.
    """
    expression = ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.LITERAL,
        ColoredPetriNetValue(ColoredPetriNetValueKind.NONE, None),
    )
    first = ColoredPetriNetTokenTemplate(ColoredPetriNetColorIdentity("a"), expression)
    second = ColoredPetriNetTokenTemplate(ColoredPetriNetColorIdentity("b"), expression)
    assert SUT((first, second)).templates == (first, second)
    with pytest.raises(ValueError):
        SUT(())
    with pytest.raises(TypeError):
        SUT([first])  # type: ignore[arg-type]
