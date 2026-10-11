r"""Software verification of ``CpnInhibitorPattern``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnInhibitorPattern`` generic
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
    CpnInhibitorPattern,
)
from projectkoios.workflow.petrinet.colored.values import CpnColorIdentity

pytestmark = pytest.mark.software_verification
SUT = CpnInhibitorPattern


def test_constructor__allowed_colors__is_nonbinding_canonical_set() -> None:
    """Evidence ID: SV-PETRINET-081

    Requirement: Inhibitor patterns admit canonical nonempty colors and bind nothing.

    Acceptance: Colors sort and the public record has no variable identity field.
    """
    a = CpnColorIdentity("a")
    b = CpnColorIdentity("b")
    pattern = SUT((b, a))
    assert pattern.allowed_color_identities == (a, b)
    assert not hasattr(pattern, "variable_identity")
    with pytest.raises(ValueError):
        SUT(())
