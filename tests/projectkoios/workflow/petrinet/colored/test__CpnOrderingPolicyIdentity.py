r"""Software verification of ``CpnOrderingPolicyIdentity``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnOrderingPolicyIdentity`` contract.

Facet and represented meaning

Nominal identity of deterministic enablement ordering semantics.

Intrinsic and cross-object scope

The exact immutable lexical boundary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored.enablement.outcomes import (
    CpnOrderingPolicyIdentity,
)

pytestmark = pytest.mark.software_verification
SUT = CpnOrderingPolicyIdentity


def test_constructor__nominality__rejects_empty_and_equal_looking_values() -> (
    None
):
    """Evidence ID: SV-PETRINET-092

    Requirement: Ordering identities are nonempty exact strings.

    Acceptance: Empty and non-string values raise their documented exceptions.
    """
    with pytest.raises(ValueError):
        SUT("")
    with pytest.raises(TypeError):
        SUT(1)  # type: ignore[arg-type]
