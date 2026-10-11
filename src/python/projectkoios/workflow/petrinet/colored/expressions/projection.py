"""Closed CPN expression projection operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ..values import (
    CpnControlRecord,
    CpnControlRecordFieldIdentity,
    CpnValue,
    CpnValueKind,
)
from .errors import CpnExpressionOperationError, CpnExpressionOperationErrorCode


@dataclass(frozen=True, slots=True)
class CpnFieldProjectorIdentity:
    """Identity of exact bounded field-projection semantics."""

    value: str = "projectkoios.workflow.cpn.field-projector:0.1"


@dataclass(frozen=True, slots=True)
class CpnFieldProjectionInput:
    """One admitted value and nonempty field path to project."""

    value: CpnValue
    field_path: tuple[CpnControlRecordFieldIdentity, ...]

    def __post_init__(self) -> None:
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")
        if type(self.field_path) is not tuple or any(
            type(item) is not CpnControlRecordFieldIdentity
            for item in self.field_path
        ):
            raise TypeError(
                "field_path must be a tuple of CpnControlRecordFieldIdentity"
            )
        if not 1 <= len(self.field_path) <= 8:
            raise ValueError("field_path must contain 1..8 identities")


@dataclass(frozen=True, slots=True)
class CpnFieldProjectionResult:
    """Exact value selected by one successful projection."""

    value: CpnValue

    def __post_init__(self) -> None:
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")


@final
class CpnFieldProjector:
    """Project only declared fields of an admitted immutable record tree."""

    __slots__ = ()

    @property
    def identity(self) -> CpnFieldProjectorIdentity:
        """Return the exact operation identity."""
        return CpnFieldProjectorIdentity()

    def execute(
        self, projection_input: CpnFieldProjectionInput
    ) -> CpnFieldProjectionResult:
        """Traverse the exact path without attribute, subscript, or callback access."""
        if type(projection_input) is not CpnFieldProjectionInput:
            raise CpnExpressionOperationError(
                CpnExpressionOperationErrorCode.INVALID_ARGUMENT,
                (),
                "projection_input must be CpnFieldProjectionInput",
            )
        value = projection_input.value
        for index, field_identity in enumerate(projection_input.field_path):
            if value.kind is not CpnValueKind.CONTROL_RECORD:
                raise CpnExpressionOperationError(
                    CpnExpressionOperationErrorCode.PROJECTION_REQUIRES_RECORD,
                    tuple(
                        item.value
                        for item in projection_input.field_path[:index]
                    ),
                    "projection step requires a control-record value",
                )
            assert type(value.value) is CpnControlRecord
            matches = tuple(
                item.value
                for item in value.value.fields
                if item.identity == field_identity
            )
            if len(matches) != 1:
                raise CpnExpressionOperationError(
                    CpnExpressionOperationErrorCode.UNKNOWN_PROJECTED_FIELD,
                    tuple(
                        item.value
                        for item in projection_input.field_path[: index + 1]
                    ),
                    "projected field is missing or duplicated",
                )
            value = matches[0]
        return CpnFieldProjectionResult(value)
