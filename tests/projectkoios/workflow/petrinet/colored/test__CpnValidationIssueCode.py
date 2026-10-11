r"""Software verification of ``CpnValidationIssueCode``.

Evidence profile: routine

Bounded artifact scope: the closed generic colored-Petri-net enumeration.

Facet and represented meaning

The class represents the accepted closed vocabulary for its owning contract.

Intrinsic and cross-object scope

Exact member spelling and order are covered. Cross-object behavior is excluded.

VVUQ and scientific exclusions

This synthetic check establishes software vocabulary only, not execution, authority,
scientific validity, UQ, or human acceptance.
"""

import pytest

from projectkoios.workflow.petrinet.colored.validation.findings import (
    CpnValidationIssueCode,
)

pytestmark = pytest.mark.software_verification
SUT = CpnValidationIssueCode


def test_property__members__matches_exact_values() -> None:
    """Evidence ID: SV-PETRINET-080

    Requirement: The public enumeration is closed to the documented exact values.

    Acceptance: Iteration returns the fixed value tuple exactly.
    """
    assert tuple(member.value for member in SUT) == (
        "unknown_color",
        "unknown_place",
        "unknown_transition",
        "color_not_allowed",
        "value_kind_not_allowed",
        "undeclared_binding_variable",
        "unbound_binding_variable",
        "duplicate_binding_variable",
        "external_output_variable_in_guard",
        "definition_identity_mismatch",
        "place_set_mismatch",
        "invalid_control_record_schema",
        "unknown_control_record_type",
        "control_record_type_not_allowed",
        "invalid_control_record_value",
        "invalid_value_expression",
    )
