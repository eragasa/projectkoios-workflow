r"""Software verification of ``ColoredPetriNetSelectionResult``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetSelectionResult`` contract.

Facet and represented meaning

Content-identified closed selected, empty, no-match, or failure outcome.

Intrinsic and cross-object scope

Variant exclusivity and identity sensitivity are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest
from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBindingSelectorIdentity,
    ColoredPetriNetSelectionOutcomeKind,
    ColoredPetriNetSelectionResult,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetSelectionResult


def test_constructor__selected_variant__derives_stable_identity() -> None:
    """Evidence ID: SV-PETRINET-114

    Requirement: A selected result binds exact enablement, policy, and binding.

    Acceptance: Equal state repeats identity and another binding changes it.
    """
    _, enablement = selection_enablement()
    assert enablement.enabled_bindings is not None
    arguments = (
        enablement.identity,
        ColoredPetriNetBindingSelectorIdentity("selector"),
        enablement.ordering_policy_identity,
        ColoredPetriNetSelectionOutcomeKind.SELECTED,
    )
    first = SUT(*arguments, selected_binding=enablement.enabled_bindings[0])
    replay = SUT(*arguments, selected_binding=enablement.enabled_bindings[0])
    second = SUT(*arguments, selected_binding=enablement.enabled_bindings[1])
    assert replay.identity == first.identity
    assert second.identity != first.identity


def test_constructor__empty_variant__rejects_selected_binding() -> None:
    """Evidence ID: SV-PETRINET-115

    Requirement: Empty outcomes contain no selected binding.

    Acceptance: A binding on ``EMPTY`` raises ``ValueError``.
    """
    _, enablement = selection_enablement()
    assert enablement.enabled_bindings is not None
    with pytest.raises(ValueError):
        SUT(
            enablement.identity,
            ColoredPetriNetBindingSelectorIdentity("selector"),
            enablement.ordering_policy_identity,
            ColoredPetriNetSelectionOutcomeKind.EMPTY,
            selected_binding=enablement.enabled_bindings[0],
        )
