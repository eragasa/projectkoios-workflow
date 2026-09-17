r"""Software verification of ``ColoredPetriNetValidationResult``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetValidationResult`` generic
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

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetValidationIssue,
    ColoredPetriNetValidationIssueCode,
    ColoredPetriNetValidationResult,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetValidationResult


def test_constructor__issues__canonicalizes_exact_findings() -> None:
    """Evidence ID: SV-PETRINET-066

    Requirement: Results retain complete findings and order them by path, code,
    identities, and message.

    Acceptance: Reversed and repeated findings store canonically and validity equals
    emptiness.
    """
    later = ColoredPetriNetValidationIssue(
        ColoredPetriNetValidationIssueCode.UNKNOWN_COLOR, ("z",), ("z",), "later"
    )
    earlier = ColoredPetriNetValidationIssue(
        ColoredPetriNetValidationIssueCode.UNKNOWN_PLACE, ("a",), ("a",), "earlier"
    )
    code_earlier = ColoredPetriNetValidationIssue(
        ColoredPetriNetValidationIssueCode.UNKNOWN_COLOR,
        ("a",),
        ("z",),
        "z-message",
    )
    identity_later = ColoredPetriNetValidationIssue(
        ColoredPetriNetValidationIssueCode.UNKNOWN_PLACE,
        ("a",),
        ("b",),
        "same",
    )
    message_later = ColoredPetriNetValidationIssue(
        ColoredPetriNetValidationIssueCode.UNKNOWN_PLACE,
        ("a",),
        ("b",),
        "z-message",
    )
    result = SUT((later, message_later, earlier, identity_later, code_earlier, earlier))
    assert result.issues == (
        code_earlier,
        earlier,
        earlier,
        identity_later,
        message_later,
        later,
    )
    assert SUT(()).is_valid
