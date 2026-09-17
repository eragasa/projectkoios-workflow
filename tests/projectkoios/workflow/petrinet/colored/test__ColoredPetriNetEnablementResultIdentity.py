r"""Software verification of ``ColoredPetriNetEnablementResultIdentity``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetEnablementResultIdentity`` contract.

Facet and represented meaning

Nominal identity of one complete enablement outcome.

Intrinsic and cross-object scope

The exact nonempty lexical boundary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetEnablementResultIdentity

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetEnablementResultIdentity


@pytest.mark.parametrize(
    ("value", "error"),
    [
        pytest.param("", ValueError, id="empty"),
        pytest.param("result", ValueError, id="malformed"),
        pytest.param("A" * 64, ValueError, id="uppercase"),
        pytest.param(1, TypeError, id="integer"),
        pytest.param(True, TypeError, id="boolean"),
        pytest.param(None, TypeError, id="none"),
    ],
)
def test_constructor__lexical_boundary__rejects_invalid_values(
    value: object, error: type[Exception]
) -> None:
    """Evidence ID: SV-PETRINET-090

    Requirement: The produced identity has one exact lowercase SHA-256 spelling.

    Acceptance: Malformed strings raise ``ValueError`` and wrong types ``TypeError``.
    """
    with pytest.raises(error):
        SUT(value)  # type: ignore[arg-type]
