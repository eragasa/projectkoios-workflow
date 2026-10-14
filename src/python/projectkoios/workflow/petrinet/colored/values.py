"""Immutable generic colored-Petri-net values and tokens.

A :class:`CpnValue` is a finite, explicitly tagged value available
to generic inscriptions and guards. A :class:`CpnToken` associates
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
import re
from dataclasses import dataclass
from enum import StrEnum

_I64_MIN = -(2**63)
_I64_MAX = 2**63 - 1
_FIELD_IDENTITY_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,127}\Z")


@dataclass(frozen=True, slots=True)
class CpnValueModelIdentity:
    """Exact scalar, control-record representation, and bound identity."""

    value: str = "projectkoios.workflow.cpn.value-model:0.1"


@dataclass(frozen=True, slots=True)
class CpnColorIdentity:
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
class CpnTokenIdentity:
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


class CpnValueKind(StrEnum):
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
    CONTROL_RECORD = "control_record"


@dataclass(frozen=True, slots=True)
class CpnValue:
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

    kind: CpnValueKind
    value: None | bool | int | float | str | tuple[str, ...] | CpnControlRecord

    def __post_init__(self) -> None:
        """Enforce the closed tagged-value invariant."""
        if not isinstance(self.kind, CpnValueKind):
            raise TypeError("value kind must be CpnValueKind")
        value = self.value
        valid = {
            CpnValueKind.NONE: value is None,
            CpnValueKind.BOOLEAN: type(value) is bool,
            CpnValueKind.INTEGER: type(value) is int,
            CpnValueKind.REAL: type(value) in (int, float),
            CpnValueKind.STRING: type(value) is str,
            CpnValueKind.STRING_SEQUENCE: isinstance(value, tuple)
            and all(type(item) is str for item in value),
            CpnValueKind.CONTROL_RECORD: type(value) is CpnControlRecord,
        }[self.kind]
        if not valid:
            raise TypeError(f"value does not match {self.kind.value} kind")
        if self.kind is CpnValueKind.INTEGER:
            assert type(value) is int
            if not _I64_MIN <= value <= _I64_MAX:
                raise ValueError("integer value must fit signed i64")
        if self.kind is CpnValueKind.REAL:
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
        if self.kind is CpnValueKind.STRING_SEQUENCE:
            assert isinstance(value, tuple)
            if any(not item for item in value):
                raise ValueError("string-sequence entries must be nonempty")


@dataclass(frozen=True, slots=True)
class CpnControlRecordTypeIdentity:
    """Nominal identity of one exact closed control-record type."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("control-record type identity must be a string")
        try:
            encoded = self.value.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ValueError(
                "control-record type identity must be ASCII"
            ) from exc
        if not 1 <= len(encoded) <= 512:
            raise ValueError(
                "control-record type identity must contain 1..512 ASCII bytes"
            )
        if self.value != self.value.strip() or any(
            ord(item) < 0x20 or ord(item) == 0x7F for item in self.value
        ):
            raise ValueError(
                "control-record type identity must be printable ASCII without "
                "surrounding whitespace"
            )


@dataclass(frozen=True, slots=True)
class CpnControlRecordFieldIdentity:
    """Nominal identity of one required control-record field."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("control-record field identity must be a string")
        if _FIELD_IDENTITY_PATTERN.fullmatch(self.value) is None:
            raise ValueError("control-record field identity has invalid syntax")


@dataclass(frozen=True, slots=True)
class CpnControlRecordFieldDefinition:
    """One required scalar, reference, or nested-record field declaration."""

    identity: CpnControlRecordFieldIdentity
    value_kind: CpnValueKind | None = None
    record_type_identity: CpnControlRecordTypeIdentity | None = None
    reference_role_identity: str | None = None

    def __post_init__(self) -> None:
        if type(self.identity) is not CpnControlRecordFieldIdentity:
            raise TypeError("identity must be CpnControlRecordFieldIdentity")
        if self.value_kind is not None and not isinstance(
            self.value_kind, CpnValueKind
        ):
            raise TypeError("value_kind must be CpnValueKind or None")
        if (
            self.record_type_identity is not None
            and type(self.record_type_identity)
            is not CpnControlRecordTypeIdentity
        ):
            raise TypeError(
                "record_type_identity must be CpnControlRecordTypeIdentity or None"
            )
        if (self.value_kind is None) == (self.record_type_identity is None):
            raise ValueError(
                "exactly one of value_kind and record_type_identity is required"
            )
        if self.value_kind is CpnValueKind.CONTROL_RECORD:
            raise ValueError("nested fields must name their exact record type")
        if self.reference_role_identity is not None:
            if type(self.reference_role_identity) is not str:
                raise TypeError(
                    "reference_role_identity must be a string or None"
                )
            if self.value_kind is not CpnValueKind.STRING:
                raise ValueError("reference fields must use STRING value kind")
            try:
                encoded_role = self.reference_role_identity.encode("ascii")
            except UnicodeEncodeError as exc:
                raise ValueError(
                    "reference_role_identity must be printable ASCII"
                ) from exc
            if (
                not 1 <= len(encoded_role) <= 512
                or self.reference_role_identity
                != self.reference_role_identity.strip()
                or any(
                    ord(item) < 0x20 or ord(item) == 0x7F
                    for item in self.reference_role_identity
                )
            ):
                raise ValueError(
                    "reference_role_identity must contain 1..512 printable "
                    "ASCII bytes without surrounding whitespace"
                )


@dataclass(frozen=True, slots=True)
class CpnControlRecordTypeDefinition:
    """One closed required-field control-record schema."""

    identity: CpnControlRecordTypeIdentity
    contract_version: int
    fields: tuple[CpnControlRecordFieldDefinition, ...]

    def __post_init__(self) -> None:
        if type(self.identity) is not CpnControlRecordTypeIdentity:
            raise TypeError("identity must be CpnControlRecordTypeIdentity")
        if type(self.contract_version) is not int:
            raise TypeError("contract_version must be an integer")
        if not 1 <= self.contract_version <= _I64_MAX:
            raise ValueError("contract_version must be a positive signed i64")
        if type(self.fields) is not tuple or any(
            type(item) is not CpnControlRecordFieldDefinition
            for item in self.fields
        ):
            raise TypeError(
                "fields must be a tuple of CpnControlRecordFieldDefinition"
            )


@dataclass(frozen=True, slots=True)
class CpnControlRecordField:
    """One immutable field and already-admitted generic CPN value."""

    identity: CpnControlRecordFieldIdentity
    value: CpnValue

    def __post_init__(self) -> None:
        if type(self.identity) is not CpnControlRecordFieldIdentity:
            raise TypeError("identity must be CpnControlRecordFieldIdentity")
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")


@dataclass(frozen=True, slots=True)
class CpnControlRecord:
    """One immutable typed control-plane record tree node."""

    type_identity: CpnControlRecordTypeIdentity
    fields: tuple[CpnControlRecordField, ...]

    def __post_init__(self) -> None:
        if type(self.type_identity) is not CpnControlRecordTypeIdentity:
            raise TypeError(
                "type_identity must be CpnControlRecordTypeIdentity"
            )
        if type(self.fields) is not tuple or any(
            type(item) is not CpnControlRecordField for item in self.fields
        ):
            raise TypeError("fields must be a tuple of CpnControlRecordField")


@dataclass(frozen=True, slots=True)
class CpnToken:
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
    counted by the containing ``CpnMarking``.
    Individually meaningful simulation attempts and results are not anonymous
    multiplicities; their Workflow-owned identities remain outside this generic
    package.
    """

    color_identity: CpnColorIdentity
    value: CpnValue
    token_identity: CpnTokenIdentity | None = None

    def __post_init__(self) -> None:
        """Validate nominal owner-local token components."""
        if type(self.color_identity) is not CpnColorIdentity:
            raise TypeError("color_identity must be CpnColorIdentity")
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")
        if self.token_identity is not None and (
            type(self.token_identity) is not CpnTokenIdentity
        ):
            raise TypeError("token_identity must be CpnTokenIdentity or None")
