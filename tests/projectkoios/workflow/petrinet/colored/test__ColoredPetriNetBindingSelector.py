r"""Software verification of ``ColoredPetriNetBindingSelector``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetBindingSelector`` ActionObject.

Facet and represented meaning

Deterministic default and explicitly permitted directed selection.

Intrinsic and cross-object scope

Canonical choice, permission, matching, empty, and failure outcomes are covered.

VVUQ and scientific exclusions

This is software verification, not firing, scientific validation, or UQ.
"""

import pytest
from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBindingSelector,
    ColoredPetriNetSelectionDirective,
    ColoredPetriNetSelectionFailureCode,
    ColoredPetriNetSelectionOutcomeKind,
    ColoredPetriNetSelectionPolicy,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetBindingSelector


def test_method__execute__default__selects_first_canonical_binding() -> None:
    """Evidence ID: SV-PETRINET-116

    Requirement: Selection without a directive has no ambient choice.

    Acceptance: The first complete enablement binding is selected exactly.
    """
    definition, enablement = selection_enablement()
    assert enablement.enabled_bindings is not None
    result = SUT().execute(definition, enablement)
    assert result.outcome is ColoredPetriNetSelectionOutcomeKind.SELECTED
    assert result.selected_binding == enablement.enabled_bindings[0]
    assert result.directive_identity is None


def test_method__execute__directed__requires_permission_and_exact_match() -> None:
    """Evidence ID: SV-PETRINET-117

    Requirement: Directed choice is explicit, definition-permitted, and exact.

    Acceptance: Canonical-only fails; directed permission selects the requested binding.
    """
    definition, enablement = selection_enablement()
    assert enablement.enabled_bindings is not None
    directive = ColoredPetriNetSelectionDirective(
        enablement.identity, enablement.enabled_bindings[1]
    )
    prohibited = SUT().execute(definition, enablement, directive)
    assert prohibited.outcome is ColoredPetriNetSelectionOutcomeKind.FAILURE
    assert prohibited.failure_code is (
        ColoredPetriNetSelectionFailureCode.DIRECTED_SELECTION_PROHIBITED
    )
    permitted, permitted_enablement = selection_enablement(
        ColoredPetriNetSelectionPolicy.DIRECTED_ALLOWED
    )
    assert permitted_enablement.enabled_bindings is not None
    permitted_directive = ColoredPetriNetSelectionDirective(
        permitted_enablement.identity, permitted_enablement.enabled_bindings[1]
    )
    selected = SUT().execute(permitted, permitted_enablement, permitted_directive)
    assert selected.outcome is ColoredPetriNetSelectionOutcomeKind.SELECTED
    assert selected.selected_binding == permitted_directive.binding
    assert selected.directive == permitted_directive
    assert selected.directive_identity == permitted_directive.identity
    policy_mismatch = SUT().execute(
        definition, permitted_enablement, permitted_directive
    )
    assert policy_mismatch.failure_code is (
        ColoredPetriNetSelectionFailureCode.DEFINITION_MISMATCH
    )


def test_method__execute__directed_absence__distinguishes_no_match_and_stale() -> None:
    """Evidence ID: SV-PETRINET-121

    Requirement: A current unmatched directive differs from a stale directive.

    Acceptance: Current absence is ``NO_MATCH``; stale correlation is ``FAILURE``.
    """
    definition, enablement = selection_enablement(
        ColoredPetriNetSelectionPolicy.DIRECTED_ALLOWED
    )
    _, other = selection_enablement(
        ColoredPetriNetSelectionPolicy.DIRECTED_ALLOWED, values=(3,)
    )
    assert other.enabled_bindings is not None
    unmatched = ColoredPetriNetSelectionDirective(
        enablement.identity, other.enabled_bindings[0]
    )
    no_match = SUT().execute(definition, enablement, unmatched)
    assert no_match.outcome is ColoredPetriNetSelectionOutcomeKind.NO_MATCH
    stale = ColoredPetriNetSelectionDirective(other.identity, other.enabled_bindings[0])
    failure = SUT().execute(definition, enablement, stale)
    assert failure.outcome is ColoredPetriNetSelectionOutcomeKind.FAILURE
    assert failure.failure_code is (
        ColoredPetriNetSelectionFailureCode.DIRECTIVE_ENABLEMENT_MISMATCH
    )


def test_method__execute__empty__distinguishes_no_enabled_binding() -> None:
    """Evidence ID: SV-PETRINET-118

    Requirement: Absence of enabled bindings is a closed nonfailure outcome.

    Acceptance: Empty enablement returns ``EMPTY`` with no selected binding.
    """
    definition, enablement = selection_enablement(values=())
    result = SUT().execute(definition, enablement)
    assert result.outcome is ColoredPetriNetSelectionOutcomeKind.EMPTY
    assert result.selected_binding is None


def test_method__execute__arguments__rejects_wrong_nominal_types() -> None:
    """Evidence ID: SV-PETRINET-119

    Requirement: Selection accepts exact definition and enablement types.

    Acceptance: Equal-looking values raise ``TypeError``.
    """
    definition, enablement = selection_enablement()
    with pytest.raises(TypeError):
        SUT().execute("definition", enablement)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        SUT().execute(definition, "enablement")  # type: ignore[arg-type]
