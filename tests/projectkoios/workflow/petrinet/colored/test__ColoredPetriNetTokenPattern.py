r"""Software verification of ``ColoredPetriNetTokenPattern``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetTokenPattern`` generic
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
    ColoredPetriNetTokenPattern,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetTokenPattern


def test_constructor__allowed_colors__canonicalizes_unique_nonempty_set() -> None:
    """Evidence ID: SV-PETRINET-052

    Requirement: A token pattern binds one variable and a canonical nonempty color set.

    Acceptance: Reversed colors sort and empty/duplicate sets reject exactly.
    """
    variable = ColoredPetriNetBindingVariableIdentity("x")
    a = ColoredPetriNetColorIdentity("a")
    b = ColoredPetriNetColorIdentity("b")
    assert SUT(variable, (b, a)).allowed_color_identities == (a, b)
    with pytest.raises(ValueError):
        SUT(variable, ())
    with pytest.raises(ValueError):
        SUT(variable, (a, a))
    with pytest.raises(TypeError):
        SUT("x", (a,))  # type: ignore[arg-type]
