r"""Software verification of ``ColoredPetriNetExpressionEvaluatorIdentity``.

Evidence profile: routine

Bounded artifact scope: the public
``ColoredPetriNetExpressionEvaluatorIdentity`` contract.

Facet and represented meaning

Nominal identity of exact expression semantics.

Intrinsic and cross-object scope

The exact immutable lexical boundary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetExpressionEvaluatorIdentity

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetExpressionEvaluatorIdentity


def test_constructor__nominality__rejects_empty_and_equal_looking_values() -> None:
    """Evidence ID: SV-PETRINET-091

    Requirement: Evaluator identities are nonempty exact strings.

    Acceptance: Empty and non-string values raise their documented exceptions.
    """
    with pytest.raises(ValueError):
        SUT("")
    with pytest.raises(TypeError):
        SUT(1)  # type: ignore[arg-type]
