r"""Software verification of ``ColoredPetriNetSelectionDirective``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetSelectionDirective`` contract.

Facet and represented meaning

Identity-bound explicit request for one enabled binding.

Intrinsic and cross-object scope

Exact nominal inputs and content-derived identity are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest
from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored import ColoredPetriNetSelectionDirective

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetSelectionDirective


def test_constructor__content_identity__is_stable_and_sensitive() -> None:
    """Evidence ID: SV-PETRINET-112

    Requirement: A directive identity binds exact enablement and requested binding.

    Acceptance: Equal content repeats the identity and another binding changes it.
    """
    _, enablement = selection_enablement()
    assert enablement.enabled_bindings is not None
    first = SUT(enablement.identity, enablement.enabled_bindings[0])
    replay = SUT(enablement.identity, enablement.enabled_bindings[0])
    second = SUT(enablement.identity, enablement.enabled_bindings[1])
    assert replay.identity == first.identity
    assert second.identity != first.identity


def test_constructor__nominality__rejects_wrong_identity_type() -> None:
    """Evidence ID: SV-PETRINET-113

    Requirement: Directive correlation uses the exact enablement identity class.

    Acceptance: Equal-looking digest text raises ``TypeError``.
    """
    _, enablement = selection_enablement()
    assert enablement.enabled_bindings is not None
    with pytest.raises(TypeError):
        SUT(enablement.identity.value, enablement.enabled_bindings[0])  # type: ignore[arg-type]
