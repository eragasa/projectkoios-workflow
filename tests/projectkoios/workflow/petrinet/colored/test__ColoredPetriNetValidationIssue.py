r"""Software verification of ``ColoredPetriNetValidationIssue``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetValidationIssue`` generic
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
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetValidationIssue


def test_constructor__finding_state__canonicalizes_related_identities() -> None:
    """Evidence ID: SV-PETRINET-083

    Requirement: Findings have nonempty paths/messages and canonically ordered lexical
    identities while retaining repeated spellings from distinct nominal types.

    Acceptance: Reversed identities sort, repeated spellings remain, and empty paths
    reject exactly.
    """
    issue = SUT(
        ColoredPetriNetValidationIssueCode.UNKNOWN_COLOR,
        ("path",),
        ("b", "a"),
        "message",
    )
    assert issue.related_identities == ("a", "b")
    repeated = SUT(issue.code, ("path",), ("a", "a"), "message")
    assert repeated.related_identities == ("a", "a")
    with pytest.raises(ValueError):
        SUT(issue.code, (), ("a",), "message")
