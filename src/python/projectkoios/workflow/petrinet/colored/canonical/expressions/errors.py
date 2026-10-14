"""Closed canonical-expression codec failures."""

from __future__ import annotations

from enum import StrEnum


class CpnExpressionCanonicalCodecErrorCode(StrEnum):
    """Closed expression canonicalization/decoding failures."""

    INVALID_ARGUMENT = "invalid_argument"
    INVALID_SHAPE = "invalid_shape"
    INVALID_EXPRESSION = "invalid_expression"
    BOUND_EXCEEDED = "bound_exceeded"
    INVALID_VALUE = "invalid_value"


class CpnExpressionCanonicalCodecError(ValueError):
    """Translated deterministic expression codec failure."""

    def __init__(
        self,
        code: CpnExpressionCanonicalCodecErrorCode,
        path: tuple[str, ...],
        message: str,
    ) -> None:
        self.code = code
        self.path = path
        self.message = message
        rendered_path = ".".join(path) if path else "<root>"
        super().__init__(f"{code.value} at {rendered_path}: {message}")
