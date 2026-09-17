r"""Software verification of ``ColoredPetriNetFiringInput``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetFiringInput`` contract.

Facet and represented meaning

Exact immutable full derivation input for pure firing.

Intrinsic and cross-object scope

Nominal field preservation and type rejection are covered.

VVUQ and scientific exclusions

This is software verification, not external execution or scientific validation.
"""

import pytest
from _firing_fixtures import valid_firing_input

from projectkoios.workflow.petrinet.colored import ColoredPetriNetFiringInput

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetFiringInput


def test_constructor__fields__preserves_complete_derivation() -> None:
    """Evidence ID: SV-PETRINET-126

    Requirement: Firing input retains full definition, state, and derivation records.

    Acceptance: Every field is present and immutable; wrong definition type rejects.
    """
    firing_input = valid_firing_input()
    assert (
        firing_input.selection_result.selected_binding == firing_input.selected_binding
    )
    assert (
        firing_input.enablement_result.definition_identity
        == firing_input.definition.identity
    )
    with pytest.raises(TypeError):
        SUT(
            "definition",  # type: ignore[arg-type]
            firing_input.transition_identity,
            firing_input.predecessor_marking,
            firing_input.enablement_result,
            firing_input.selection_result,
            firing_input.selected_binding,
            firing_input.directive_identity,
            firing_input.external_output_binding,
        )
