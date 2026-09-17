r"""Software verification of ``ColoredPetriNetEnablementFailureIdentity``.

Evidence profile: routine

Bounded artifact scope: the public
``ColoredPetriNetEnablementFailureIdentity`` contract.

Facet and represented meaning

Nominal identity of one failed enablement result.

Intrinsic and cross-object scope

Exact binding to the distinct result identity is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetEnablementFailureIdentity,
    ColoredPetriNetEnablementResultIdentity,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetEnablementFailureIdentity


def test_constructor__correlation__requires_exact_result_identity() -> None:
    """Evidence ID: SV-PETRINET-104

    Requirement: Failure and result identities are distinct but exactly correlated.

    Acceptance: The nominal result identity is retained; a string is rejected.
    """
    result_identity = ColoredPetriNetEnablementResultIdentity("0" * 64)
    assert SUT(result_identity).result_identity is result_identity
    with pytest.raises(TypeError):
        SUT("result")  # type: ignore[arg-type]
