r"""Software verification of ``CpnSelectionOutcomeKind``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnSelectionOutcomeKind`` enum.

Facet and represented meaning

Closed selected, empty, no-match, and failure variants.

Intrinsic and cross-object scope

The exact outcome vocabulary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored.selection import (
    CpnSelectionOutcomeKind,
)

pytestmark = pytest.mark.software_verification
SUT = CpnSelectionOutcomeKind


def test_property__members__matches_exact_values() -> None:
    """Evidence ID: SV-PETRINET-107

    Requirement: Selection outcomes are closed and distinguish absence from failure.

    Acceptance: Names and values equal the fixed oracle.
    """
    assert tuple((item.name, item.value) for item in SUT) == (
        ("SELECTED", "selected"),
        ("EMPTY", "empty"),
        ("NO_MATCH", "no_match"),
        ("FAILURE", "failure"),
    )
