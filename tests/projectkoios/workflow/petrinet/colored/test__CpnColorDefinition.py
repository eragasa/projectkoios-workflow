r"""Software verification of ``CpnColorDefinition``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnColorDefinition`` generic
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
    CpnColorDefinition,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = CpnColorDefinition


def test_constructor__allowed_value_kinds__canonicalizes_unique_nonempty_set() -> (
    None
):
    """Evidence ID: SV-PETRINET-059

    Requirement: A color admits a canonical nonempty unique set of value kinds.

    Acceptance: Reversed kinds sort; empty and duplicate tuples reject exactly.
    """
    identity = CpnColorIdentity("color")
    color = SUT(identity, (CpnValueKind.STRING, CpnValueKind.INTEGER))
    assert color.allowed_value_kinds == (
        CpnValueKind.INTEGER,
        CpnValueKind.STRING,
    )
    with pytest.raises(ValueError):
        SUT(identity, ())
    with pytest.raises(ValueError):
        SUT(identity, (CpnValueKind.NONE,) * 2)
