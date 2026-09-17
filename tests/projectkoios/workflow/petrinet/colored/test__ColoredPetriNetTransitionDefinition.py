r"""Software verification of ``ColoredPetriNetTransitionDefinition``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetTransitionDefinition`` generic
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
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetTransitionDefinition,
    ColoredPetriNetTransitionIdentity,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetTransitionDefinition


def test_constructor__variable_roles__preserves_order_and_disjointness() -> None:
    """Evidence ID: SV-PETRINET-060

    Requirement: Input/external-output variables are ordered, unique, and disjoint.

    Acceptance: Exact order stores and duplicate/overlapping declarations reject.
    """
    z = ColoredPetriNetBindingVariableIdentity("z")
    a = ColoredPetriNetBindingVariableIdentity("a")
    guard = ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.TRUE)
    transition = SUT(ColoredPetriNetTransitionIdentity("t"), (z, a), (), guard)
    assert transition.input_variable_identities == (z, a)
    with pytest.raises(ValueError):
        SUT(transition.identity, (z, z), (), guard)
    with pytest.raises(ValueError):
        SUT(transition.identity, (z,), (z,), guard)
