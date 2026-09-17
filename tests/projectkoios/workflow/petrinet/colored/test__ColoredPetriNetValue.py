r"""Software verification of ``ColoredPetriNetValue``.

Evidence profile: routine

Bounded artifact scope: the tagged generic value DataObject.

Facet and represented meaning

The class represents one finite, exactly tagged generic Petri-net value.

Intrinsic and cross-object scope

The tests cover the closed tags, exact scalar boundaries, canonical binary64
storage, tuple immutability, and exception taxonomy intrinsic to the value.

VVUQ and scientific exclusions

These synthetic exact checks establish software behavior only. They establish no
numerical verification, scientific validation, uncertainty quantification, or
physical interpretation.
"""

import math
from dataclasses import FrozenInstanceError

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = ColoredPetriNetValue


@pytest.mark.parametrize(
    ("kind", "value", "expected"),
    [
        pytest.param(ColoredPetriNetValueKind.NONE, None, None, id="none"),
        pytest.param(ColoredPetriNetValueKind.BOOLEAN, True, True, id="boolean"),
        pytest.param(ColoredPetriNetValueKind.INTEGER, -3, -3, id="integer"),
        pytest.param(ColoredPetriNetValueKind.REAL, 3, 3.0, id="integer_real"),
        pytest.param(ColoredPetriNetValueKind.REAL, -2.5, -2.5, id="float_real"),
        pytest.param(ColoredPetriNetValueKind.STRING, "x", "x", id="string"),
        pytest.param(
            ColoredPetriNetValueKind.STRING_SEQUENCE,
            ("x", "x"),
            ("x", "x"),
            id="ordered_duplicate_strings",
        ),
    ],
)
def test_constructor__tagged_values__preserves_canonical_state(
    kind: ColoredPetriNetValueKind,
    value: None | bool | int | float | str | tuple[str, ...],
    expected: None | bool | int | float | str | tuple[str, ...],
) -> None:
    """Evidence ID: SV-PETRINET-009

    Requirement: Every closed value tag admits its documented exact representation.

    Acceptance: Each named partition stores the exact canonical expected value.
    """
    assert SUT(kind, value).value == expected


@pytest.mark.parametrize(
    ("kind", "value"),
    [
        pytest.param(ColoredPetriNetValueKind.NONE, False, id="none_boolean"),
        pytest.param(ColoredPetriNetValueKind.BOOLEAN, 1, id="boolean_integer"),
        pytest.param(ColoredPetriNetValueKind.INTEGER, True, id="integer_boolean"),
        pytest.param(ColoredPetriNetValueKind.REAL, True, id="real_boolean"),
        pytest.param(ColoredPetriNetValueKind.REAL, "1.0", id="real_numeric_string"),
        pytest.param(ColoredPetriNetValueKind.STRING, 1, id="string_integer"),
        pytest.param(
            ColoredPetriNetValueKind.STRING_SEQUENCE,
            ["x"],
            id="sequence_list",
        ),
        pytest.param(
            ColoredPetriNetValueKind.STRING_SEQUENCE,
            (1,),
            id="sequence_integer_member",
        ),
    ],
)
def test_constructor__semantic_types__rejects_tag_mismatches(
    kind: ColoredPetriNetValueKind,
    value: object,
) -> None:
    """Evidence ID: SV-PETRINET-010

    Requirement: Tags reject implicit coercion and mismatched semantic types.

    Acceptance: Every named mismatch raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT(kind, value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("kind", "value"),
    [
        pytest.param(
            ColoredPetriNetValueKind.INTEGER,
            -(2**63) - 1,
            id="integer_below_i64",
        ),
        pytest.param(
            ColoredPetriNetValueKind.INTEGER,
            2**63,
            id="integer_above_i64",
        ),
        pytest.param(ColoredPetriNetValueKind.REAL, math.inf, id="positive_infinity"),
        pytest.param(ColoredPetriNetValueKind.REAL, math.nan, id="nan"),
        pytest.param(ColoredPetriNetValueKind.REAL, 10**400, id="binary64_overflow"),
        pytest.param(
            ColoredPetriNetValueKind.STRING_SEQUENCE,
            ("",),
            id="empty_sequence_member",
        ),
    ],
)
def test_constructor__value_invariants__rejects_invalid_values(
    kind: ColoredPetriNetValueKind,
    value: int | float | tuple[str, ...],
) -> None:
    """Evidence ID: SV-PETRINET-011

    Requirement: Correctly typed values satisfy the documented finite boundaries.

    Acceptance: Every named invalid-value partition raises ``ValueError`` exactly.
    """
    with pytest.raises(ValueError):
        SUT(kind, value)


def test_constructor__kind_type__rejects_non_enum_tag() -> None:
    """Evidence ID: SV-PETRINET-020

    Requirement: The value tag uses the exact owner-local enum rather than a
    matching string.

    Acceptance: A lexical tag raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT("string", "value")  # type: ignore[arg-type]


def test_constructor__immutability__produces_frozen_record() -> None:
    """Evidence ID: SV-PETRINET-021

    Requirement: A generic tagged value is operationally immutable.

    Acceptance: Assigning its public value field raises ``FrozenInstanceError``.
    """
    value = SUT(ColoredPetriNetValueKind.STRING, "value")
    with pytest.raises(FrozenInstanceError):
        value.value = "changed"  # type: ignore[misc]


def test_constructor__real_canonicalization__uses_finite_binary64() -> None:
    """Evidence ID: SV-PETRINET-012

    Requirement: Integer-valued real inputs use the documented binary64 boundary.

    Acceptance: The stored value is an exact built-in float with Python's binary64
    rounding, and signed-i64 integer boundaries remain accepted as integers.
    """
    rounded = SUT(ColoredPetriNetValueKind.REAL, 2**53 + 1).value
    minimum = SUT(ColoredPetriNetValueKind.INTEGER, -(2**63)).value
    maximum = SUT(ColoredPetriNetValueKind.INTEGER, 2**63 - 1).value
    assert type(rounded) is float
    assert rounded == float(2**53)
    assert (minimum, maximum) == (-(2**63), 2**63 - 1)
