r"""Software verification of ``CpnBinding``.

Evidence profile: routine

Bounded artifact scope: one immutable ordered generic transition variable/value binding.

Facet and represented meaning

The class binds a nominal transition to a unique sequence of variable/value assignments
in definition-declared order.

Intrinsic and cross-object scope

Order preservation, variable uniqueness, nominal typing, and immutability are intrinsic.
Agreement with a transition definition belongs to later cross-object validation.

VVUQ and scientific exclusions

These synthetic checks establish binding software behavior only, not enablement,
firing, numerical verification, scientific validation, or uncertainty quantification.
"""

from dataclasses import FrozenInstanceError

import pytest

from projectkoios.workflow.petrinet.colored.bindings import (
    CpnBinding,
    CpnBindingAssignment,
)
from projectkoios.workflow.petrinet.colored.definitions import (
    CpnTransitionIdentity,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = CpnBinding


def make_assignment(variable: str, value: int) -> CpnBindingAssignment:
    """Evidence ID: Owns no identifier; supports binding evidence.

    Requirement: Binding tests need explicit variable/value assignments.

    Acceptance: The helper returns the corresponding public assignment.
    """
    return CpnBindingAssignment(
        CpnBindingVariableIdentity(variable),
        CpnValue(CpnValueKind.INTEGER, value),
    )


def test_constructor__assignment_order__preserves_definition_owned_order() -> (
    None
):
    """Evidence ID: SV-PETRINET-035

    Requirement: Binding order is supplied by the definition owner and must not be
    lexically rewritten by the DataObject.

    Acceptance: A nonlexical unique assignment tuple is retained exactly.
    """
    z = make_assignment("z", 1)
    a = make_assignment("a", 2)
    binding = SUT(CpnTransitionIdentity("transition"), (z, a))
    assert binding.assignments == (z, a)


def test_constructor__immutability__produces_frozen_record() -> None:
    """Evidence ID: SV-PETRINET-042

    Requirement: A transition binding is operationally immutable.

    Acceptance: Assigning its assignment tuple raises ``FrozenInstanceError``.
    """
    binding = SUT(CpnTransitionIdentity("transition"), ())
    with pytest.raises(FrozenInstanceError):
        binding.assignments = ()  # type: ignore[misc]


def test_constructor__variable_identity__rejects_duplicates() -> None:
    """Evidence ID: SV-PETRINET-036

    Requirement: One variable appears at most once in a complete transition binding.

    Acceptance: Repeating a nominal variable identity raises ``ValueError`` exactly.
    """
    with pytest.raises(ValueError):
        SUT(
            CpnTransitionIdentity("transition"),
            (make_assignment("x", 1), make_assignment("x", 2)),
        )


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(("transition", ()), id="lexical_transition_identity"),
        pytest.param(
            (CpnTransitionIdentity("transition"), []),
            id="mutable_assignments",
        ),
        pytest.param(
            (CpnTransitionIdentity("transition"), ("assignment",)),
            id="non_assignment_member",
        ),
    ],
)
def test_constructor__nominal_types__rejects_wrong_types(
    arguments: tuple[object, object],
) -> None:
    """Evidence ID: SV-PETRINET-037

    Requirement: Bindings accept exact nominal transition identities and immutable
    assignment tuples.

    Acceptance: Every named wrong-type partition raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT(*arguments)  # type: ignore[arg-type]
