"""Closed control-record validation findings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CpnControlRecordValidationIssueCode(StrEnum):
    """Closed findings from type-graph and record-value validation."""

    TOO_MANY_TYPE_DEFINITIONS = "too_many_type_definitions"
    DUPLICATE_TYPE_IDENTITY = "duplicate_type_identity"
    INVALID_FIELD_COUNT = "invalid_field_count"
    DUPLICATE_FIELD_IDENTITY = "duplicate_field_identity"
    NONCANONICAL_FIELD_ORDER = "noncanonical_field_order"
    UNKNOWN_RECORD_TYPE = "unknown_record_type"
    CYCLIC_TYPE_GRAPH = "cyclic_type_graph"
    TYPE_GRAPH_TOO_DEEP = "type_graph_too_deep"
    RECORD_TOO_DEEP = "record_too_deep"
    RECORD_TOO_MANY_NODES = "record_too_many_nodes"
    CYCLIC_RECORD_VALUE = "cyclic_record_value"
    FIELD_SET_MISMATCH = "field_set_mismatch"
    FIELD_VALUE_KIND_MISMATCH = "field_value_kind_mismatch"
    NESTED_RECORD_TYPE_MISMATCH = "nested_record_type_mismatch"
    STRING_TOO_LARGE = "string_too_large"
    INVALID_UTF8_STRING = "invalid_utf8_string"
    STRING_SEQUENCE_TOO_LARGE = "string_sequence_too_large"
    INVALID_REFERENCE_IDENTITY = "invalid_reference_identity"


@dataclass(frozen=True, slots=True)
class CpnControlRecordValidationIssue:
    """One deterministic directly inspectable validation finding."""

    code: CpnControlRecordValidationIssueCode
    path: tuple[str, ...]
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.code, CpnControlRecordValidationIssueCode):
            raise TypeError("code must be CpnControlRecordValidationIssueCode")
        if type(self.path) is not tuple or any(
            type(item) is not str for item in self.path
        ):
            raise TypeError("path must be a tuple of strings")
        if type(self.message) is not str or not self.message:
            raise TypeError("message must be a nonempty string")


@dataclass(frozen=True, slots=True)
class CpnControlRecordValidationResult:
    """Complete canonically ordered record validation findings."""

    issues: tuple[CpnControlRecordValidationIssue, ...]

    def __post_init__(self) -> None:
        if type(self.issues) is not tuple or any(
            type(item) is not CpnControlRecordValidationIssue
            for item in self.issues
        ):
            raise TypeError(
                "issues must be a tuple of CpnControlRecordValidationIssue"
            )
        ordered = [
            ((item.path, item.code.value, item.message), ordinal, item)
            for ordinal, item in enumerate(self.issues)
        ]
        ordered.sort()
        object.__setattr__(self, "issues", tuple(item[2] for item in ordered))

    @property
    def is_valid(self) -> bool:
        """Return whether validation produced no finding."""
        return not self.issues
