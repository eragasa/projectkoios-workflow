r"""Software verification of ``CpnBindingAssignment``.

Evidence profile: routine

Bounded artifact scope: one immutable generic binding variable/value association.

Facet and represented meaning

The class associates one nominal definition-owned variable with one tagged value.

Intrinsic and cross-object scope

Exact nominal component preservation and type rejection are intrinsic. Definition
membership and variable compatibility remain cross-object behavior.

VVUQ and scientific exclusions

These synthetic checks establish software association behavior only, not numerical
verification, scientific validation, uncertainty quantification, or physical meaning.
"""

from dataclasses import FrozenInstanceError

import pytest

from projectkoios.workflow.petrinet.colored.bindings import CpnBindingAssignment
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = CpnBindingAssignment


def test_constructor__fields__preserves_nominal_variable_and_value() -> None:
    """Evidence ID: SV-PETRINET-033

    Requirement: A binding assignment preserves its exact nominal variable and tagged
    value.

    Acceptance: Both public fields retain the supplied objects by identity.
    """
    variable = CpnBindingVariableIdentity("x")
    value = CpnValue(CpnValueKind.INTEGER, 1)
    assignment = SUT(variable, value)
    assert assignment.variable_identity is variable
    assert assignment.value is value


def test_constructor__immutability__produces_frozen_record() -> None:
    """Evidence ID: SV-PETRINET-041

    Requirement: A binding assignment is operationally immutable.

    Acceptance: Assigning its value raises ``FrozenInstanceError``.
    """
    assignment = SUT(
        CpnBindingVariableIdentity("x"),
        CpnValue(CpnValueKind.INTEGER, 1),
    )
    with pytest.raises(FrozenInstanceError):
        assignment.value = CpnValue(  # type: ignore[misc]
            CpnValueKind.INTEGER, 2
        )


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(
            ("x", CpnValue(CpnValueKind.INTEGER, 1)),
            id="lexical_variable_identity",
        ),
        pytest.param(
            (CpnBindingVariableIdentity("x"), 1),
            id="untagged_value",
        ),
    ],
)
def test_constructor__nominal_types__rejects_wrong_types(
    arguments: tuple[object, object],
) -> None:
    """Evidence ID: SV-PETRINET-034

    Requirement: Assignment components use exact generic nominal types.

    Acceptance: Every named wrong-type partition raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT(*arguments)  # type: ignore[arg-type]
