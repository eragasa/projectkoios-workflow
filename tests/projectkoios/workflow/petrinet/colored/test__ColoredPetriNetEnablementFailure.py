r"""Software verification of ``ColoredPetriNetEnablementFailure``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetEnablementFailure`` contract.

Facet and represented meaning

Structured operational failure with no enabled-binding payload.

Intrinsic and cross-object scope

Immutable fields, stable codes, diagnostics, and claim boundaries are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetEnablementFailure,
    ColoredPetriNetEnablementFailureCode,
    ColoredPetriNetEnablementFailureIdentity,
    ColoredPetriNetEnablementResultIdentity,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetEnablementFailure


def test_constructor__closed_failure__retains_exact_fields() -> None:
    """Evidence ID: SV-PETRINET-094

    Requirement: A failure retains its phase, conditions, diagnostic, and boundary.

    Acceptance: Every supplied field is preserved exactly and state is frozen.
    """
    failure = SUT(
        ColoredPetriNetEnablementFailureIdentity(
            ColoredPetriNetEnablementResultIdentity("0" * 64)
        ),
        ColoredPetriNetEnablementFailureCode.INVALID_MARKING,
        "marking_validation",
        "compatible marking",
        "validation findings",
        "not evaluated",
    )
    assert failure.operation_phase == "marking_validation"
    assert failure.expected_condition == "compatible marking"
    assert failure.observed_condition == "validation findings"
    assert failure.diagnostic == "not evaluated"
    assert failure.validation_issues == ()
    assert failure.claim_boundary == (
        "software enablement only",
        "no firing or external effect",
        "no scientific acceptance",
    )
    with pytest.raises(AttributeError):
        failure.diagnostic = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "field",
    [
        pytest.param("operation_phase", id="phase"),
        pytest.param("expected_condition", id="expected"),
        pytest.param("observed_condition", id="observed"),
        pytest.param("diagnostic", id="diagnostic"),
    ],
)
def test_constructor__text_fields__rejects_empty_values(field: str) -> None:
    """Evidence ID: SV-PETRINET-095

    Requirement: Required diagnostic fields are explicit and nonempty.

    Acceptance: Empty required text raises ``ValueError``.
    """
    field_names = (
        "operation_phase",
        "expected_condition",
        "observed_condition",
        "diagnostic",
    )
    values = ["phase", "expected", "observed", "diagnostic"]
    values[field_names.index(field)] = ""
    with pytest.raises(ValueError):
        SUT(
            ColoredPetriNetEnablementFailureIdentity(
                ColoredPetriNetEnablementResultIdentity("0" * 64)
            ),
            ColoredPetriNetEnablementFailureCode.INVALID_MARKING,
            values[0],
            values[1],
            values[2],
            values[3],
        )
