"""Closed CPN structural validation findings and results."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CpnValidationIssueCode(StrEnum):
    """Stable semantic codes for v2 structural findings.

    Attributes
    ----------
    UNKNOWN_COLOR
        A referenced color is absent from the definition.
    UNKNOWN_PLACE
        An arc references a place absent from the definition.
    UNKNOWN_TRANSITION
        An arc references a transition absent from the definition.
    COLOR_NOT_ALLOWED
        A pattern, template, or token color is not admitted by its place.
    VALUE_KIND_NOT_ALLOWED
        A token value kind is not admitted by its color definition.
    UNDECLARED_BINDING_VARIABLE
        A pattern or expression references a variable outside its permitted role.
    UNBOUND_BINDING_VARIABLE
        A declared input variable has no valid consume/read binder.
    DUPLICATE_BINDING_VARIABLE
        A declared input variable has multiple valid consume/read binders.
    EXTERNAL_OUTPUT_VARIABLE_IN_GUARD
        A guard references a variable reserved for external output.
    DEFINITION_IDENTITY_MISMATCH
        A marking identifies a different definition from the supplied definition.
    PLACE_SET_MISMATCH
        A marking does not contain exactly the definition's place set.
    """

    UNKNOWN_COLOR = "unknown_color"
    UNKNOWN_PLACE = "unknown_place"
    UNKNOWN_TRANSITION = "unknown_transition"
    COLOR_NOT_ALLOWED = "color_not_allowed"
    VALUE_KIND_NOT_ALLOWED = "value_kind_not_allowed"
    UNDECLARED_BINDING_VARIABLE = "undeclared_binding_variable"
    UNBOUND_BINDING_VARIABLE = "unbound_binding_variable"
    DUPLICATE_BINDING_VARIABLE = "duplicate_binding_variable"
    EXTERNAL_OUTPUT_VARIABLE_IN_GUARD = "external_output_variable_in_guard"
    DEFINITION_IDENTITY_MISMATCH = "definition_identity_mismatch"
    PLACE_SET_MISMATCH = "place_set_mismatch"
    INVALID_CONTROL_RECORD_SCHEMA = "invalid_control_record_schema"
    UNKNOWN_CONTROL_RECORD_TYPE = "unknown_control_record_type"
    CONTROL_RECORD_TYPE_NOT_ALLOWED = "control_record_type_not_allowed"
    INVALID_CONTROL_RECORD_VALUE = "invalid_control_record_value"
    INVALID_VALUE_EXPRESSION = "invalid_value_expression"


@dataclass(frozen=True, slots=True)
class CpnValidationIssue:
    """One immutable structural validation finding.

    Parameters
    ----------
    code
        Stable v2 semantic issue code.
    path
        Nonempty exact structural path from the validated root.
    related_identities
        Nonempty lexical identities stored canonically. Repeated lexical values are
        retained when distinct nominal identity classes share the same spelling.
    message
        Nonempty sanitized diagnostic with no authority or scientific meaning.

    Raises
    ------
    TypeError
        A field has the wrong semantic type or a collection is mutable.
    ValueError
        A required tuple or string is empty.
    """

    code: CpnValidationIssueCode
    path: tuple[str, ...]
    related_identities: tuple[str, ...]
    message: str

    def __post_init__(self) -> None:
        """Validate immutable issue state and canonicalize related identities."""
        if not isinstance(self.code, CpnValidationIssueCode):
            raise TypeError("code must be CpnValidationIssueCode")
        for field_name in ("path", "related_identities"):
            values = getattr(self, field_name)
            if type(values) is not tuple or any(
                type(item) is not str for item in values
            ):
                raise TypeError(f"{field_name} must be a tuple of strings")
            if not values or any(not item for item in values):
                raise ValueError(f"{field_name} entries must be nonempty")
        if type(self.message) is not str:
            raise TypeError("message must be a string")
        if not self.message:
            raise ValueError("message must not be empty")
        object.__setattr__(
            self, "related_identities", tuple(sorted(self.related_identities))
        )


@dataclass(frozen=True, slots=True)
class CpnValidationResult:
    """Canonical immutable structural findings from one validation operation.

    Parameters
    ----------
    issues
        Complete findings canonicalized by path, code, related identities, and
        message. Repeated exact findings are retained when repeated malformed
        occurrences produce them.

    Raises
    ------
    TypeError
        ``issues`` is mutable or contains a wrong semantic type.
    """

    issues: tuple[CpnValidationIssue, ...]

    def __post_init__(self) -> None:
        """Validate and canonically order complete findings without collapsing them."""
        if type(self.issues) is not tuple or any(
            type(issue) is not CpnValidationIssue for issue in self.issues
        ):
            raise TypeError("issues must be a tuple of CpnValidationIssue")
        ordered = [
            (
                (
                    issue.path,
                    issue.code.value,
                    issue.related_identities,
                    issue.message,
                ),
                ordinal,
                issue,
            )
            for ordinal, issue in enumerate(self.issues)
        ]
        ordered.sort()
        object.__setattr__(self, "issues", tuple(item[2] for item in ordered))

    @property
    def is_valid(self) -> bool:
        """Whether no declared structural issue was found."""
        return not self.issues
