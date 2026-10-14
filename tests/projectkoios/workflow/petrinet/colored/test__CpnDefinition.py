r"""Software verification of ``CpnDefinition``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnDefinition`` generic
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

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnArcDefinition,
    CpnArcIdentity,
    CpnDefinition,
    CpnDefinitionIdentity,
    CpnPlaceIdentity,
    CpnSelectionPolicy,
    CpnTransitionDefinition,
    CpnTransitionIdentity,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnGuardExpression,
    CpnGuardOperator,
    CpnInputInscription,
    CpnInputMode,
    CpnTokenPattern,
)
from projectkoios.workflow.petrinet.colored.values import CpnColorIdentity

pytestmark = pytest.mark.software_verification
SUT = CpnDefinition


def transition(name: str) -> CpnTransitionDefinition:
    """Return one unconditional transition; this helper owns no identifier.

    Evidence ID: Helper owns no identifier.

    Requirement: Support aggregate definition tests without an evidence claim.

    Acceptance: Return one public transition with no declared variables.
    """
    return CpnTransitionDefinition(
        CpnTransitionIdentity(name),
        (),
        (),
        CpnGuardExpression(CpnGuardOperator.TRUE),
    )


def test_constructor__components__canonicalizes_without_reordering_priority() -> (
    None
):
    """Evidence ID: SV-PETRINET-062

    Requirement: Components are canonical while priority remains explicit policy order.

    Acceptance: Reversed transitions sort without changing the declared priority tuple.
    """
    a = transition("a")
    b = transition("b")
    definition = SUT(
        CpnDefinitionIdentity("definition"),
        (),
        (),
        (b, a),
        (),
        (b.identity, a.identity),
    )
    assert definition.transitions == (a, b)
    assert definition.transition_priority == (b.identity, a.identity)
    assert definition.selection_policy is (
        CpnSelectionPolicy.DETERMINISTIC_ONLY
    )


def test_constructor__selection_policy__requires_closed_enum() -> None:
    """Evidence ID: SV-PETRINET-120

    Requirement: Directed-selection permission is explicit definition-owned policy.

    Acceptance: The closed enum is retained and a string is rejected.
    """
    item = transition("transition")
    args = (
        CpnDefinitionIdentity("definition"),
        (),
        (),
        (item,),
        (),
        (item.identity,),
    )
    assert (
        SUT(*args, CpnSelectionPolicy.DIRECTED_ALLOWED).selection_policy
        is CpnSelectionPolicy.DIRECTED_ALLOWED
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
    args = (CpnDefinitionIdentity("definition"), (), (), (a, b), ())
    with pytest.raises(ValueError):
        SUT(*args, (a.identity,))
    with pytest.raises(ValueError):
        SUT(*args, (a.identity, a.identity))
    with pytest.raises(ValueError):
        SUT(*args, (a.identity, CpnTransitionIdentity("extra")))


def test_constructor__component_identities__rejects_duplicates() -> None:
    """Evidence ID: SV-PETRINET-064

    Requirement: Every component identity is unique within its family.

    Acceptance: Duplicate transition and duplicate arc identities reject exactly.
    """
    item = transition("transition")
    identity = CpnDefinitionIdentity("definition")
    with pytest.raises(ValueError):
        SUT(identity, (), (), (item, item), (), (item.identity,))
    pattern = CpnTokenPattern(
        CpnBindingVariableIdentity("x"),
        (CpnColorIdentity("color"),),
    )
    arc = CpnArcDefinition(
        CpnArcIdentity("arc"),
        CpnPlaceIdentity("place"),
        item.identity,
        CpnInputInscription(CpnInputMode.CONSUME, (pattern,)),
    )
    with pytest.raises(ValueError):
        SUT(identity, (), (), (item,), (arc, arc), (item.identity,))
