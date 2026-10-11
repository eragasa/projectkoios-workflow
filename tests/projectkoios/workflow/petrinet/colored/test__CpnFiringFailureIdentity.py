r"""Software verification of ``CpnFiringFailureIdentity``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnFiringFailureIdentity`` contract.

Facet and represented meaning

Nominal identity of one failed firing result.

Intrinsic and cross-object scope

Exact result-identity correlation is covered.

VVUQ and scientific exclusions

This is software verification, not external execution or scientific validation.
"""

import pytest

from projectkoios.workflow.petrinet.colored.firing import (
    CpnFiringFailureIdentity,
    CpnFiringResultIdentity,
)

pytestmark = pytest.mark.software_verification
SUT = CpnFiringFailureIdentity


def test_constructor__correlation__requires_exact_result_identity() -> None:
    """Evidence ID: SV-PETRINET-136

    Requirement: Failure identity binds one exact firing-result identity.

    Acceptance: Exact identity is retained and digest text rejected.
    """
    identity = CpnFiringResultIdentity("0" * 64)
    assert SUT(identity).result_identity is identity
    with pytest.raises(TypeError):
        SUT(identity.value)  # type: ignore[arg-type]
