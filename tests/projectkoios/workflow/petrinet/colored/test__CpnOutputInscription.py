r"""Software verification of ``CpnOutputInscription``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnOutputInscription`` generic
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

from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnOutputInscription,
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
SUT = CpnOutputInscription


def test_constructor__templates__preserves_nonempty_order() -> None:
    """Evidence ID: SV-PETRINET-054

    Requirement: Output inscriptions preserve nonempty ordered template multiplicity.

    Acceptance: Two templates remain ordered; empty and mutable inputs reject.
    """
    expression = CpnValueExpression(
        CpnValueExpressionKind.LITERAL,
        CpnValue(CpnValueKind.NONE, None),
    )
    first = CpnTokenTemplate(CpnColorIdentity("a"), expression)
    second = CpnTokenTemplate(CpnColorIdentity("b"), expression)
    assert SUT((first, second)).templates == (first, second)
    with pytest.raises(ValueError):
        SUT(())
    with pytest.raises(TypeError):
        SUT([first])  # type: ignore[arg-type]
