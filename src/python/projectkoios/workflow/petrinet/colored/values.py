"""Immutable generic colored-Petri-net values and tokens.

A :class:`ColoredPetriNetValue` is a finite, explicitly tagged value available
to generic inscriptions and guards. A :class:`ColoredPetriNetToken` associates
one such value with a color and, when individual correlation is required, a
nominal token identity. Indistinguishable-token multiplicity belongs exclusively
to the marking that contains tokens; it is not stored on a token.

These records contain no Workflow, scientific-result, calculator, persistence,
authority, or external-effect meaning. Construction tests are software
verification and establish no numerical verification, scientific validation, or
uncertainty quantification.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

_I64_MIN = -(2**63)
_I64_MAX = 2**63 - 1


@dataclass(frozen=True, slots=True)
class ColoredPetriNetColorIdentity:
    """Nominal identity of one token color in a colored-Petri-net definition.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity. No canonical encoding or wire
        representation is selected by this in-memory contract.

    Raises
    ------
    TypeError
        ``value`` is not an exact built-in string.
    ValueError
        ``value`` is empty.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the owner-local lexical boundary."""
        if type(self.value) is not str:
            raise TypeError("color identity value must be a string")
        if not self.value:
            raise ValueError("color identity value must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetTokenIdentity:
    """Nominal identity of one individually correlated generic token.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity. No canonical encoding or wire
        representation is selected by this in-memory contract.

    Raises
    ------
    TypeError
        ``value`` is not an exact built-in string.
    ValueError
        ``value`` is empty.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the owner-local lexical boundary."""
        if type(self.value) is not str:
            raise TypeError("token identity value must be a string")
        if not self.value:
            raise ValueError("token identity value must not be empty")


class ColoredPetriNetValueKind(StrEnum):
    """Closed tags for generic colored-Petri-net scalar values.

    Attributes
    ----------
    NONE
        The sole admitted value is ``None``.
    BOOLEAN
        The admitted value is an exact built-in Boolean.
    INTEGER
        The admitted value is a signed 64-bit built-in integer.
    REAL
        The admitted input is an exact built-in integer or finite float and is
        stored as finite IEEE-754 binary64.
    STRING
        The admitted value is an exact built-in string.
    STRING_SEQUENCE
        The admitted value is an ordered tuple of nonempty built-in strings;
        duplicates are meaningful and preserved.
    """

    NONE = "none"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    REAL = "real"
    STRING = "string"
    STRING_SEQUENCE = "string_sequence"


@dataclass(frozen=True, slots=True)
class ColoredPetriNetValue:
    """One explicitly tagged immutable generic colored-Petri-net value.

    Parameters
    ----------
    kind
        Exact enum member selecting the active value representation.
    value
        Immutable value matching ``kind``. Numeric strings and Boolean-as-number
        inputs are rejected.

    Raises
    ------
    TypeError
        A field has the wrong semantic type.
    ValueError
        An integer is outside signed 64-bit range, a real is nonfinite or
        overflows binary64, or a string-sequence member is empty.

    Notes
    -----
    Integer inputs to ``REAL`` are canonicalized to built-in ``float`` and may
    round to the nearest representable binary64 value. This is a generic finite
    software representation, not a physical quantity or numerical tolerance.
    """

    kind: ColoredPetriNetValueKind
    value: None | bool | int | float | str | tuple[str, ...]

    def __post_init__(self) -> None:
        """Enforce the closed tagged-value invariant."""
        if not isinstance(self.kind, ColoredPetriNetValueKind):
            raise TypeError("value kind must be ColoredPetriNetValueKind")
        value = self.value
        valid = {
            ColoredPetriNetValueKind.NONE: value is None,
            ColoredPetriNetValueKind.BOOLEAN: type(value) is bool,
            ColoredPetriNetValueKind.INTEGER: type(value) is int,
            ColoredPetriNetValueKind.REAL: type(value) in (int, float),
            ColoredPetriNetValueKind.STRING: type(value) is str,
            ColoredPetriNetValueKind.STRING_SEQUENCE: isinstance(value, tuple)
            and all(type(item) is str for item in value),
        }[self.kind]
        if not valid:
            raise TypeError(f"value does not match {self.kind.value} kind")
        if self.kind is ColoredPetriNetValueKind.INTEGER:
            assert type(value) is int
            if not _I64_MIN <= value <= _I64_MAX:
                raise ValueError("integer value must fit signed i64")
        if self.kind is ColoredPetriNetValueKind.REAL:
            if type(value) is int:
                try:
                    canonical_real = float(value)
                except OverflowError as exc:
                    raise ValueError("real value overflows binary64") from exc
            else:
                assert type(value) is float
                canonical_real = value
            if not math.isfinite(canonical_real):
                raise ValueError("real value must be finite binary64")
            object.__setattr__(self, "value", canonical_real)
        if self.kind is ColoredPetriNetValueKind.STRING_SEQUENCE:
            assert isinstance(value, tuple)
            if any(not item for item in value):
                raise ValueError("string-sequence entries must be nonempty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetToken:
    """One color-qualified immutable generic token value.

    Parameters
    ----------
    color_identity
        Nominal identity of the token's color.
    value
        Generic immutable value carried by the token.
    token_identity
        Optional nominal identity used when individual correlation matters.
        ``None`` denotes an indistinguishable token value whose multiplicity is
        represented solely by its containing marking.

    Raises
    ------
    TypeError
        A field has the wrong nominal type.

    Notes
    -----
    The token deliberately carries no multiplicity. Equal anonymous tokens are
    counted by the containing ``ColoredPetriNetMarking``.
    Individually meaningful simulation attempts and results are not anonymous
    multiplicities; their Workflow-owned identities remain outside this generic
    package.
    """

    color_identity: ColoredPetriNetColorIdentity
    value: ColoredPetriNetValue
    token_identity: ColoredPetriNetTokenIdentity | None = None

    def __post_init__(self) -> None:
        """Validate nominal owner-local token components."""
        if type(self.color_identity) is not ColoredPetriNetColorIdentity:
            raise TypeError("color_identity must be ColoredPetriNetColorIdentity")
        if type(self.value) is not ColoredPetriNetValue:
            raise TypeError("value must be ColoredPetriNetValue")
        if self.token_identity is not None and (
            type(self.token_identity) is not ColoredPetriNetTokenIdentity
        ):
            raise TypeError(
                "token_identity must be ColoredPetriNetTokenIdentity or None"
            )
