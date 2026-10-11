"""Bounded control-record value/schema validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ...values import (
    CpnControlRecord,
    CpnControlRecordTypeDefinition,
    CpnValueKind,
)
from .findings import (
    CpnControlRecordValidationIssue,
    CpnControlRecordValidationIssueCode,
    CpnControlRecordValidationResult,
)
from .type_graph import (
    CpnControlRecordTypeGraphValidationInput,
    CpnControlRecordTypeGraphValidator,
)


@dataclass(frozen=True, slots=True)
class CpnControlRecordSchemaValidatorIdentity:
    """Identity of exact bounded record-value validation semantics."""

    value: str = "projectkoios.workflow.cpn.control-record-schema-validator:0.1"

    def __post_init__(self) -> None:
        if type(self.value) is not str or not self.value:
            raise TypeError("validator identity must be a nonempty string")


@dataclass(frozen=True, slots=True)
class CpnControlRecordSchemaValidationInput:
    """Exact retained schemas and one record value to validate."""

    record: CpnControlRecord
    definitions: tuple[CpnControlRecordTypeDefinition, ...]

    def __post_init__(self) -> None:
        if type(self.record) is not CpnControlRecord:
            raise TypeError("record must be CpnControlRecord")
        if type(self.definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.definitions
        ):
            raise TypeError(
                "definitions must be a tuple of CpnControlRecordTypeDefinition"
            )


@final
class CpnControlRecordSchemaValidator:
    """Directly validate one finite record against exact retained schemas."""

    __slots__ = ()

    @property
    def identity(self) -> CpnControlRecordSchemaValidatorIdentity:
        """Return the exact semantics identity."""
        return CpnControlRecordSchemaValidatorIdentity()

    def execute(
        self, validation_input: CpnControlRecordSchemaValidationInput
    ) -> CpnControlRecordValidationResult:
        """Return all schema, type, tree, lexical, and bound findings."""
        if type(validation_input) is not CpnControlRecordSchemaValidationInput:
            raise TypeError(
                "validation_input must be CpnControlRecordSchemaValidationInput"
            )
        graph_result = CpnControlRecordTypeGraphValidator().execute(
            CpnControlRecordTypeGraphValidationInput(
                validation_input.definitions
            )
        )
        if not graph_result.is_valid:
            return graph_result
        by_identity = {
            item.identity: item for item in validation_input.definitions
        }
        issues: list[CpnControlRecordValidationIssue] = []
        nodes = 0
        stack: list[
            tuple[CpnControlRecord, tuple[str, ...], int, frozenset[int]]
        ] = [
            (
                validation_input.record,
                (validation_input.record.type_identity.value,),
                1,
                frozenset(),
            )
        ]
        while stack:
            record, path, depth, ancestors = stack.pop()
            marker = id(record)
            if marker in ancestors:
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.CYCLIC_RECORD_VALUE,
                        path,
                        "control-record values must be finite acyclic trees",
                    )
                )
                continue
            if depth > 8:
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.RECORD_TOO_DEEP,
                        path,
                        "control-record nesting exceeds depth 8",
                    )
                )
                continue
            nodes += 1
            if nodes > 256:
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.RECORD_TOO_MANY_NODES,
                        (validation_input.record.type_identity.value,),
                        "control-record tree exceeds 256 record and scalar nodes",
                    )
                )
                break
            definition = by_identity.get(record.type_identity)
            if definition is None:
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.UNKNOWN_RECORD_TYPE,
                        path,
                        "record uses an unknown record type",
                    )
                )
                continue
            actual_names = tuple(item.identity.value for item in record.fields)
            expected_names = tuple(
                item.identity.value for item in definition.fields
            )
            if len(record.fields) > 64:
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.INVALID_FIELD_COUNT,
                        path,
                        "a control record may contain at most 64 fields",
                    )
                )
            if len(set(actual_names)) != len(actual_names):
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.DUPLICATE_FIELD_IDENTITY,
                        path,
                        "control-record field identities must be unique",
                    )
                )
            if actual_names != tuple(sorted(actual_names)):
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.NONCANONICAL_FIELD_ORDER,
                        path,
                        "control-record fields must use lexical identity order",
                    )
                )
            if actual_names != expected_names:
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.FIELD_SET_MISMATCH,
                        path,
                        "record fields must equal the complete required schema",
                    )
                )
                continue
            for field_definition, field in zip(
                definition.fields, record.fields, strict=True
            ):
                field_path = path + (field.identity.value,)
                value = field.value
                target = field_definition.record_type_identity
                if target is not None:
                    if value.kind is not CpnValueKind.CONTROL_RECORD:
                        issues.append(
                            CpnControlRecordValidationIssue(
                                CpnControlRecordValidationIssueCode.FIELD_VALUE_KIND_MISMATCH,
                                field_path,
                                "nested-record field has a scalar value",
                            )
                        )
                        continue
                    assert type(value.value) is CpnControlRecord
                    if value.value.type_identity != target:
                        issues.append(
                            CpnControlRecordValidationIssue(
                                CpnControlRecordValidationIssueCode.NESTED_RECORD_TYPE_MISMATCH,
                                field_path,
                                "nested record has the wrong exact record type",
                            )
                        )
                        continue
                    stack.append(
                        (
                            value.value,
                            field_path,
                            depth + 1,
                            ancestors | {marker},
                        )
                    )
                    continue
                nodes += 1
                if nodes > 256:
                    issues.append(
                        CpnControlRecordValidationIssue(
                            CpnControlRecordValidationIssueCode.RECORD_TOO_MANY_NODES,
                            (validation_input.record.type_identity.value,),
                            "control-record tree exceeds 256 record and scalar nodes",
                        )
                    )
                    stack.clear()
                    break
                if value.kind is not field_definition.value_kind:
                    issues.append(
                        CpnControlRecordValidationIssue(
                            CpnControlRecordValidationIssueCode.FIELD_VALUE_KIND_MISMATCH,
                            field_path,
                            "field value kind differs from its schema",
                        )
                    )
                    continue
                if value.kind is CpnValueKind.STRING:
                    assert type(value.value) is str
                    try:
                        encoded_string = value.value.encode("utf-8")
                    except UnicodeEncodeError:
                        issues.append(
                            CpnControlRecordValidationIssue(
                                CpnControlRecordValidationIssueCode.INVALID_UTF8_STRING,
                                field_path,
                                "string is not encodable as valid UTF-8",
                            )
                        )
                    else:
                        if len(encoded_string) > 4096:
                            issues.append(
                                CpnControlRecordValidationIssue(
                                    CpnControlRecordValidationIssueCode.STRING_TOO_LARGE,
                                    field_path,
                                    "string exceeds 4096 UTF-8 bytes",
                                )
                            )
                if value.kind is CpnValueKind.STRING_SEQUENCE:
                    assert type(value.value) is tuple
                    if len(value.value) > 256:
                        issues.append(
                            CpnControlRecordValidationIssue(
                                CpnControlRecordValidationIssueCode.STRING_SEQUENCE_TOO_LARGE,
                                field_path,
                                "string sequence exceeds 256 entries",
                            )
                        )
                    for index, item in enumerate(value.value):
                        try:
                            encoded_item = item.encode("utf-8")
                        except UnicodeEncodeError:
                            issues.append(
                                CpnControlRecordValidationIssue(
                                    CpnControlRecordValidationIssueCode.INVALID_UTF8_STRING,
                                    field_path + (str(index),),
                                    "string-sequence entry is not valid UTF-8",
                                )
                            )
                        else:
                            if len(encoded_item) > 4096:
                                issues.append(
                                    CpnControlRecordValidationIssue(
                                        CpnControlRecordValidationIssueCode.STRING_TOO_LARGE,
                                        field_path + (str(index),),
                                        "string-sequence entry exceeds 4096 UTF-8 bytes",
                                    )
                                )
                if field_definition.reference_role_identity is not None:
                    assert type(value.value) is str
                    try:
                        encoded_reference = value.value.encode("ascii")
                    except UnicodeEncodeError:
                        encoded_reference = b""
                    if (
                        not 1 <= len(encoded_reference) <= 512
                        or value.value != value.value.strip()
                        or any(
                            ord(item) < 0x20 or ord(item) == 0x7F
                            for item in value.value
                        )
                    ):
                        issues.append(
                            CpnControlRecordValidationIssue(
                                CpnControlRecordValidationIssueCode.INVALID_REFERENCE_IDENTITY,
                                field_path,
                                "reference identity violates its lexical contract",
                            )
                        )
        return CpnControlRecordValidationResult(tuple(issues))
