"""Closed CPN expression construction operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ..control.records.findings import CpnControlRecordValidationIssue
from ..control.records.schema import (
    CpnControlRecordSchemaValidationInput,
    CpnControlRecordSchemaValidator,
)
from ..values import (
    CpnControlRecord,
    CpnControlRecordField,
    CpnControlRecordTypeDefinition,
    CpnControlRecordTypeIdentity,
)
from .errors import CpnExpressionOperationError, CpnExpressionOperationErrorCode


@dataclass(frozen=True, slots=True)
class CpnControlRecordConstructorIdentity:
    """Identity of exact closed record-construction semantics."""

    value: str = "projectkoios.workflow.cpn.control-record-constructor:0.1"


@dataclass(frozen=True, slots=True)
class CpnControlRecordConstructionInput:
    """Exact type, fields, and retained schemas for record construction."""

    type_identity: CpnControlRecordTypeIdentity
    fields: tuple[CpnControlRecordField, ...]
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...]

    def __post_init__(self) -> None:
        if type(self.type_identity) is not CpnControlRecordTypeIdentity:
            raise TypeError(
                "type_identity must be CpnControlRecordTypeIdentity"
            )
        if type(self.fields) is not tuple or any(
            type(item) is not CpnControlRecordField for item in self.fields
        ):
            raise TypeError("fields must be a tuple of CpnControlRecordField")
        if type(self.type_definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.type_definitions
        ):
            raise TypeError(
                "type_definitions must be a tuple of "
                "CpnControlRecordTypeDefinition"
            )


@dataclass(frozen=True, slots=True)
class CpnControlRecordConstructionResult:
    """One constructed and schema-validated immutable record."""

    record: CpnControlRecord

    def __post_init__(self) -> None:
        if type(self.record) is not CpnControlRecord:
            raise TypeError("record must be CpnControlRecord")


@final
class CpnControlRecordConstructor:
    """Construct a closed record and require exact schema validation."""

    __slots__ = ()

    @property
    def identity(self) -> CpnControlRecordConstructorIdentity:
        """Return the exact operation identity."""
        return CpnControlRecordConstructorIdentity()

    def execute(
        self, construction_input: CpnControlRecordConstructionInput
    ) -> CpnControlRecordConstructionResult:
        """Construct without owner classes, callables, imports, or resolution."""
        if type(construction_input) is not CpnControlRecordConstructionInput:
            raise CpnExpressionOperationError(
                CpnExpressionOperationErrorCode.INVALID_ARGUMENT,
                (),
                "construction_input must be CpnControlRecordConstructionInput",
            )
        known = {
            item.identity: item for item in construction_input.type_definitions
        }
        definition = known.get(construction_input.type_identity)
        if definition is None:
            raise CpnExpressionOperationError(
                CpnExpressionOperationErrorCode.UNKNOWN_RECORD_TYPE,
                (construction_input.type_identity.value,),
                "constructor references an unknown record type",
            )
        expected = tuple(item.identity for item in definition.fields)
        actual = tuple(item.identity for item in construction_input.fields)
        if actual != expected:
            raise CpnExpressionOperationError(
                CpnExpressionOperationErrorCode.CONSTRUCTOR_FIELD_MISMATCH,
                (construction_input.type_identity.value,),
                "constructor fields differ from the complete lexical schema",
            )
        record = CpnControlRecord(
            construction_input.type_identity, construction_input.fields
        )
        validation = CpnControlRecordSchemaValidator().execute(
            CpnControlRecordSchemaValidationInput(
                record, construction_input.type_definitions
            )
        )
        if not validation.is_valid:
            first: CpnControlRecordValidationIssue = validation.issues[0]
            raise CpnExpressionOperationError(
                CpnExpressionOperationErrorCode.RECORD_SCHEMA_VIOLATION,
                first.path,
                first.code.value,
            )
        return CpnControlRecordConstructionResult(record)
