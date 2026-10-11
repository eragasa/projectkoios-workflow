r"""Software verification of ``CpnArcDefinition``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnArcDefinition`` generic
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
    CpnPlaceIdentity,
    CpnTransitionIdentity,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnInputInscription,
    CpnInputMode,
    CpnOutputInscription,
    CpnTokenPattern,
    CpnTokenTemplate,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnValue,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = CpnArcDefinition


def test_constructor__direction_variant__requires_exactly_one_inscription() -> (
    None
):
    """Evidence ID: SV-PETRINET-061

    Requirement: Arc direction is represented by exactly one inscription variant.

    Acceptance: Input constructs while absent and duplicated variants reject exactly.
    """
    pattern = CpnTokenPattern(
        CpnBindingVariableIdentity("x"),
        (CpnColorIdentity("color"),),
    )
    inscription = CpnInputInscription(CpnInputMode.CONSUME, (pattern,))
    args = (
        CpnArcIdentity("arc"),
        CpnPlaceIdentity("place"),
        CpnTransitionIdentity("transition"),
    )
    assert SUT(*args, inscription).input_inscription is inscription
    with pytest.raises(ValueError):
        SUT(*args)
    expression = CpnValueExpression(
        CpnValueExpressionKind.LITERAL,
        CpnValue(CpnValueKind.NONE, None),
    )
    output = CpnOutputInscription(
        (CpnTokenTemplate(CpnColorIdentity("color"), expression),)
    )
    with pytest.raises(ValueError):
        SUT(*args, inscription, output_inscription=output)
