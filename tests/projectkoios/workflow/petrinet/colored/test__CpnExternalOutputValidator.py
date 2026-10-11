"""Direct tests for exact already-admitted external-output validation."""

from projectkoios.workflow.petrinet.colored.bindings import (
    CpnBinding,
    CpnBindingAssignment,
)
from projectkoios.workflow.petrinet.colored.external_outputs import (
    CpnExternalOutputValidationInput,
    CpnExternalOutputValidationIssueCode,
    CpnExternalOutputValidator,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
)

from _validation_fixtures import valid_definition


def test_execute__accepts_exact_declared_external_binding() -> None:
    """Exact transition and variable order is valid."""
    definition = valid_definition()
    transition = definition.transitions[0]
    binding = CpnBinding(
        transition.identity,
        (
            CpnBindingAssignment(
                transition.external_output_variable_identities[0],
                CpnValue(CpnValueKind.INTEGER, 2),
            ),
        ),
    )
    assert (
        CpnExternalOutputValidator()
        .execute(
            CpnExternalOutputValidationInput(
                definition, transition.identity, binding
            )
        )
        .is_valid
    )


def test_execute__rejects_incomplete_binding() -> None:
    """Missing external values never default or resolve."""
    definition = valid_definition()
    transition = definition.transitions[0]
    result = CpnExternalOutputValidator().execute(
        CpnExternalOutputValidationInput(
            definition,
            transition.identity,
            CpnBinding(transition.identity, ()),
        )
    )
    assert result.issues[0].code is (
        CpnExternalOutputValidationIssueCode.VARIABLE_SET_MISMATCH
    )
