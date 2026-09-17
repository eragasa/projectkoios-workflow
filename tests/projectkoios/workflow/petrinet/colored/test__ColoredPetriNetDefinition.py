r"""Software verification of ``ColoredPetriNetDefinition``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetDefinition`` generic
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
    ColoredPetriNetArcDefinition,
    ColoredPetriNetArcIdentity,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetColorIdentity,
    ColoredPetriNetDefinition,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetInputInscription,
    ColoredPetriNetInputMode,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetSelectionPolicy,
    ColoredPetriNetTokenPattern,
    ColoredPetriNetTransitionDefinition,
    ColoredPetriNetTransitionIdentity,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetDefinition


def transition(name: str) -> ColoredPetriNetTransitionDefinition:
    """Return one unconditional transition; this helper owns no identifier.

    Evidence ID: Helper owns no identifier.

    Requirement: Support aggregate definition tests without an evidence claim.

    Acceptance: Return one public transition with no declared variables.
    """
    return ColoredPetriNetTransitionDefinition(
        ColoredPetriNetTransitionIdentity(name),
        (),
        (),
        ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.TRUE),
    )


def test_constructor__components__canonicalizes_without_reordering_priority() -> None:
    """Evidence ID: SV-PETRINET-062

    Requirement: Components are canonical while priority remains explicit policy order.

    Acceptance: Reversed transitions sort without changing the declared priority tuple.
    """
    a = transition("a")
    b = transition("b")
    definition = SUT(
        ColoredPetriNetDefinitionIdentity("definition"),
        (),
        (),
        (b, a),
        (),
        (b.identity, a.identity),
    )
    assert definition.transitions == (a, b)
    assert definition.transition_priority == (b.identity, a.identity)
    assert definition.selection_policy is (
        ColoredPetriNetSelectionPolicy.DETERMINISTIC_ONLY
    )


def test_constructor__selection_policy__requires_closed_enum() -> None:
    """Evidence ID: SV-PETRINET-120

    Requirement: Directed-selection permission is explicit definition-owned policy.

    Acceptance: The closed enum is retained and a string is rejected.
    """
    item = transition("transition")
    args = (
        ColoredPetriNetDefinitionIdentity("definition"),
        (),
        (),
        (item,),
        (),
        (item.identity,),
    )
    assert (
        SUT(*args, ColoredPetriNetSelectionPolicy.DIRECTED_ALLOWED).selection_policy
        is ColoredPetriNetSelectionPolicy.DIRECTED_ALLOWED
    )
    with pytest.raises(TypeError):
        SUT(*args, "directed_allowed")  # type: ignore[arg-type]


def test_constructor__priority__requires_total_exact_permutation() -> None:
    """Evidence ID: SV-PETRINET-063

    Requirement: Priority contains every declared transition exactly once.

    Acceptance: Missing, duplicate, and extra identities raise ``ValueError``.
    """
    a = transition("a")
    b = transition("b")
    args = (ColoredPetriNetDefinitionIdentity("definition"), (), (), (a, b), ())
    with pytest.raises(ValueError):
        SUT(*args, (a.identity,))
    with pytest.raises(ValueError):
        SUT(*args, (a.identity, a.identity))
    with pytest.raises(ValueError):
        SUT(*args, (a.identity, ColoredPetriNetTransitionIdentity("extra")))


def test_constructor__component_identities__rejects_duplicates() -> None:
    """Evidence ID: SV-PETRINET-064

    Requirement: Every component identity is unique within its family.

    Acceptance: Duplicate transition and duplicate arc identities reject exactly.
    """
    item = transition("transition")
    identity = ColoredPetriNetDefinitionIdentity("definition")
    with pytest.raises(ValueError):
        SUT(identity, (), (), (item, item), (), (item.identity,))
    pattern = ColoredPetriNetTokenPattern(
        ColoredPetriNetBindingVariableIdentity("x"),
        (ColoredPetriNetColorIdentity("color"),),
    )
    arc = ColoredPetriNetArcDefinition(
        ColoredPetriNetArcIdentity("arc"),
        ColoredPetriNetPlaceIdentity("place"),
        item.identity,
        ColoredPetriNetInputInscription(ColoredPetriNetInputMode.CONSUME, (pattern,)),
    )
    with pytest.raises(ValueError):
        SUT(identity, (), (), (item,), (arc, arc), (item.identity,))
