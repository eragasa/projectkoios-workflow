"""Closed CPN expression errors operations."""

from __future__ import annotations

from enum import StrEnum


class CpnExpressionOperationErrorCode(StrEnum):
    """Closed failures from projection, construction, and evaluation."""

    INVALID_ARGUMENT = "invalid_argument"
    EXPRESSION_TOO_DEEP = "expression_too_deep"
    EXPRESSION_TOO_MANY_NODES = "expression_too_many_nodes"
    CYCLIC_EXPRESSION = "cyclic_expression"
    UNBOUND_VARIABLE = "unbound_variable"
    PROJECTION_REQUIRES_RECORD = "projection_requires_record"
    UNKNOWN_PROJECTED_FIELD = "unknown_projected_field"
    UNKNOWN_RECORD_TYPE = "unknown_record_type"
    CONSTRUCTOR_FIELD_MISMATCH = "constructor_field_mismatch"
    RECORD_SCHEMA_VIOLATION = "record_schema_violation"


class CpnExpressionOperationError(ValueError):
    """One inspectable closed expression-operation failure."""

    def __init__(
        self,
        code: CpnExpressionOperationErrorCode,
        path: tuple[str, ...],
        diagnostic: str,
    ) -> None:
        if not isinstance(code, CpnExpressionOperationErrorCode):
            raise TypeError("code must be CpnExpressionOperationErrorCode")
        if type(path) is not tuple or any(
            type(item) is not str for item in path
        ):
            raise TypeError("path must be a tuple of strings")
        if type(diagnostic) is not str or not diagnostic:
            raise TypeError("diagnostic must be a nonempty string")
        self.code = code
        self.path = path
        self.diagnostic = diagnostic
        super().__init__(
            f"{code.value} at {'.'.join(path) or '$'}: {diagnostic}"
        )
